from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum

from characters.character import Character

# ACTIVE effects are currently applying. Refresh-required effects enter RESIDUAL when their
# source stops supplying them; residual effects keep applying temporarily after that point.
class TimedEffectState(Enum):
    ACTIVE = 0
    RESIDUAL = 1

# Base class for an effect that persists across frames and owns its own tick/residual timers.
# The processor tracks these instances and manages source appearance/disappearance for
# refresh-required effects.
@dataclass(kw_only=True)
class TimedCharacterEffect(ABC):
    character: Character

    # Identifies one ongoing effect for processor tracking. Matching keys refresh an existing
    # effect rather than starting a duplicate timer.
    effect_key: str
    tick_interval_secs: float

    state: TimedEffectState = TimedEffectState.ACTIVE
    
    residual_secs_base: float = 0.0

    # Effects supplied by refresh sources, such as regions, are refreshed every frame.
    # Persistent effects must be added through add_non_refresh_effect(), whose returned key
    # the caller retains for later removal.
    requires_refresh: bool = True

    # Runtime counters belong to this persistent effect instance, not to fresh effect
    # descriptions supplied by refresh sources each frame.
    residual_secs_left: float = field(init=False)
    interval_elapsed_secs: float = field(init=False)

    @abstractmethod
    def update(self, delta_secs: float) -> None:
        pass

    def __post_init__(self) -> None:
        self.residual_secs_left = self.residual_secs_base
        self.interval_elapsed_secs = 0

    # A source reappeared before this effect's residual period expired. Resume active ticking
    # with a fresh tick interval and a restored residual-duration budget.
    def reactivate_from_residual(self) -> None:
        self.state = TimedEffectState.ACTIVE

        # reset all internal timers
        self.interval_elapsed_secs = 0
        self.residual_secs_left = self.residual_secs_base

    def enter_residual_phase(self) -> None:
        # The supplying source disappeared, but this effect remains in effect for its configured
        # residual duration. Reset the damage interval so residual timing begins fresh.
        self.state = TimedEffectState.RESIDUAL

        #reset all internal timers
        self.residual_secs_left = self.residual_secs_base
        self.interval_elapsed_secs = 0

# Timed effect that repeatedly applies absolute health damage while active or residual.
@dataclass(kw_only=True)
class TimedDamageEffectAbs(TimedCharacterEffect):

    damage_per_interval: int

    def update(self, delta_secs: float) -> None:
        # usually we care about the whole interval, except if residual (or other timed phase in future) expired
        # during this interval, we only want to count the time the effect was active for the measurement

        time_effect_was_active = delta_secs

        if self.state == TimedEffectState.RESIDUAL:
            # this is where we need to account for the delta_secs being longer than the effect for timer purposes
            # clip the timer so it never expands beyond when this effect could even possibly had been active
            time_effect_was_active = min(self.residual_secs_left, time_effect_was_active)
            self.residual_secs_left -= time_effect_was_active

        secs_since_last_trigger = self.interval_elapsed_secs + time_effect_was_active
        
        if secs_since_last_trigger >= self.tick_interval_secs:
            self.interval_elapsed_secs = secs_since_last_trigger - self.tick_interval_secs
            # purposefully not handling a case where a multiple of intervals pass in one frame with a burst of immediate 
            # damage. i don't think that will ever happen irl and also not sure i'd like the effect anyway
            self.character.take_damage(self.damage_per_interval)
        else:
            self.interval_elapsed_secs = secs_since_last_trigger


# Tracks timed-effect instances across frames. Sources may refresh effects several times
# per frame; the game loop calls process() once after all sources have reported.
class TimedCharacterEffectProcessor:

    def __init__(self):
        self.tracked_timed_effects: list[TimedCharacterEffect] = []
        self._refreshed_effect_keys_this_frame: set[str] = set()

        # Monotonically increasing prefix makes each processor-generated persistent-effect key unique.
        self.key_tail: int = 0

    def _find_effect_by_key(self, in_key: str) -> TimedCharacterEffect | None:
        return next((x for x in self.tracked_timed_effects if x.effect_key == in_key), None)

    def _add_key_header(self, in_key: str) -> str:
        # Prefix a caller-provided descriptive key with this processor's unique counter.
        out_str = f"{self.key_tail}_" + in_key 
        self.key_tail += 1
        return out_str

    # Add a persistent effect and return its generated key. The caller retains that key and
    # later passes it to remove_effect_by_key() when the effect should end.
    def add_non_refresh_effect(self, effect: TimedCharacterEffect) -> str:
        
        if effect.requires_refresh == True:
            raise ValueError(f"add_non_refresh_effect can only be sent non-refresh effects, received {effect}")
        
        effect.effect_key = self._add_key_header(effect.effect_key)
        self.tracked_timed_effects.append(effect)
        return effect.effect_key

    def remove_effect_by_key(self, in_key: str) -> bool:
        # Remove a tracked effect at caller request. Return whether a tracked effect used that key.
        for effect in self.tracked_timed_effects:
            if effect.effect_key == in_key:
                self.tracked_timed_effects.remove(effect)
                return True

        return False

    # Record refresh-required effects currently supplied by one source. Multiple sources may call
    # this per frame; persistent effects must use add_non_refresh_effect() instead.
    def refresh_effects(self, effects: Sequence[TimedCharacterEffect]) -> None:
        for effect in effects:

            if effect.requires_refresh == False:
                raise ValueError(f"refresh_effects can only be sent refresh-required effects, received {effect}")
        
            pre_existing = self._find_effect_by_key(effect.effect_key)

            # if it's already in the tracked list, flip if it was residual 
            if pre_existing is not None:
                if pre_existing.state == TimedEffectState.RESIDUAL:
                    pre_existing.reactivate_from_residual()
            else:
                # if it's not already in the list, add it for processing
                self.tracked_timed_effects.append(effect)

            # in all cases mark that we saw it
            self._refreshed_effect_keys_this_frame.add(effect.effect_key)

    # Once per frame, move absent refresh-required effects into residual or remove them,
    # advance every remaining effect, then prune expired residual effects.
    def process(self, delta_secs: float) -> None:

        prune_key_set = set()

        # Refresh-required effects absent from every refresh source this frame either enter
        # residual or end immediately.
        for effect in self.tracked_timed_effects:
            if (effect.effect_key not in self._refreshed_effect_keys_this_frame
                    and effect.requires_refresh is True):
                if effect.state == TimedEffectState.ACTIVE:
                        if effect.residual_secs_base > 0:
                            effect.enter_residual_phase()
                        else:
                            prune_key_set.add(effect.effect_key)

        if prune_key_set:
            self.tracked_timed_effects = [effect
                                          for effect in self.tracked_timed_effects
                                          if effect.effect_key not in prune_key_set]

        self._refreshed_effect_keys_this_frame.clear()
        prune_key_set.clear()

        # update all remaining items and generate second prune list (effects in residual phase that have expired)
        for effect in self.tracked_timed_effects:
            effect.update(delta_secs)

            if effect.state == TimedEffectState.RESIDUAL and effect.residual_secs_left <= 0:
                prune_key_set.add(effect.effect_key)

        # prune effects in residual phase that have timed out
        if prune_key_set:
            self.tracked_timed_effects = [effect
                                          for effect in self.tracked_timed_effects
                                          if effect.effect_key not in prune_key_set]












