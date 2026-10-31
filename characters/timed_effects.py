from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum

from characters.character import Character

# ACTIVE effects are currently applying. Refresh-required effects enter RESIDUAL when their
# source stops supplying them; residual effects keep applying temporarily after that point.
class RefreshRequiredTimedEffectState(Enum):
    ACTIVE = 0
    RESIDUAL = 1

# Base class for an effect that persists across frames and owns the tick,
# residual, or non-refresh expiration timers appropriate to its lifecycle.
# The processor tracks these instances and manages source appearance/disappearance for
# refresh-required effects.
@dataclass(kw_only=True)
class TimedCharacterEffect(ABC):
    character: Character

    # Identifies one ongoing effect for processor tracking. Matching keys refresh an existing
    # effect rather than starting a duplicate timer.
    effect_key: str
    tick_interval_secs: float

    # Only refresh-required effects use ACTIVE and RESIDUAL state. A non-refresh
    # effect stays active until its creator removes it or its own timer expires.
    state: RefreshRequiredTimedEffectState = RefreshRequiredTimedEffectState.ACTIVE
    
    residual_secs_base: float = 0.0

    # Effects supplied by refresh sources, such as regions, must be reported every
    # frame they are active. Non-refresh effects are added once; they either expire
    # from their own timer or remain until their creator removes them by key.
    requires_refresh: bool = True

    # Optional lifecycle for a non-refresh effect that should end automatically.
    # The base duration is configuration; the remaining duration is runtime state.
    no_refresh_req_is_timed: bool = False
    no_refresh_req_timer_base: float = 0.0

    # Runtime counters belong to this persistent effect instance, not to fresh effect
    # descriptions supplied by refresh sources each frame.
    residual_secs_left: float = field(init=False)
    interval_elapsed_secs: float = field(init=False)
    # Counts down from no_refresh_req_timer_base while this automatically expiring
    # non-refresh effect is processed.
    no_refresh_req_timer_secs_left: float = field(init=False)

    def __post_init__(self) -> None:
        self.residual_secs_left = self.residual_secs_base
        self.no_refresh_req_timer_secs_left = self.no_refresh_req_timer_base
        self.interval_elapsed_secs = 0

        # Reject contradictory lifecycle settings instead of allowing an effect whose
        # refresh, residual, and expiration behavior is unclear.
        if (self.requires_refresh is True
            and (self.no_refresh_req_is_timed is True or self.no_refresh_req_timer_base != 0)):
            raise ValueError(f"Illegal value combination for TimedCharacterEffect (mixing refresh and non refresh): {self}")
        elif (self.requires_refresh is False
              and self.no_refresh_req_is_timed is True
              and self.no_refresh_req_timer_base <= 0):
            raise ValueError(f"Illegal value combination for TimedCharacterEffect (non-refresh, timed with no timer val): {self}")
        elif (self.requires_refresh is False
              and self.no_refresh_req_is_timed is False
              and self.no_refresh_req_timer_base != 0):
            raise ValueError(f"Illegal value combination for TimedCharacterEffect (non-refresh, untimed with timer val): {self}")

    # A source reappeared before this effect's residual period expired. Resume active ticking
    # with a fresh tick interval and a restored residual-duration budget.
    def reactivate_from_residual(self) -> None:
        self.state = RefreshRequiredTimedEffectState.ACTIVE

        # reset all internal timers
        self.interval_elapsed_secs = 0
        self.residual_secs_left = self.residual_secs_base

    def enter_residual_phase(self) -> None:
        # The supplying source disappeared, but this effect remains in effect for its configured
        # residual duration. Reset the damage interval so residual timing begins fresh.
        self.state = RefreshRequiredTimedEffectState.RESIDUAL

        #reset all internal timers
        self.residual_secs_left = self.residual_secs_base
        self.interval_elapsed_secs = 0

    def update(self, delta_secs: float) -> None:
        # Advance this effect's applicable lifetime and tick timers. When a full
        # interval has elapsed, delegate the gameplay-specific result to apply_effect().
        time_effect_was_active = delta_secs

        # Decrease the active lifecycle timer when this effect is in a timed phase.
        if self.state == RefreshRequiredTimedEffectState.RESIDUAL:
            # Clip the elapsed time so a residual effect cannot count time after it expired.
            time_effect_was_active = min(self.residual_secs_left, time_effect_was_active)
            self.residual_secs_left -= time_effect_was_active
        elif self.requires_refresh is False and self.no_refresh_req_is_timed:
            time_effect_was_active = min(self.no_refresh_req_timer_secs_left, time_effect_was_active)
            self.no_refresh_req_timer_secs_left -= time_effect_was_active

        secs_since_last_trigger = self.interval_elapsed_secs + time_effect_was_active

        if secs_since_last_trigger >= self.tick_interval_secs:
            self.interval_elapsed_secs = secs_since_last_trigger - self.tick_interval_secs
            # Intentionally do not apply several missed intervals as one immediate burst.
            self.apply_effect()
        else:
            self.interval_elapsed_secs = secs_since_last_trigger

    @abstractmethod
    def apply_effect(self) -> None:
        # Subclasses implement the gameplay-specific consequence of one completed
        # interval; the parent owns all shared timing and lifecycle work.
        pass

# Timed effect that repeatedly applies absolute health damage while it remains
# tracked, respecting either residual duration or non-refresh expiration.
@dataclass(kw_only=True)
class TimedDamageEffectAbs(TimedCharacterEffect):

    damage_per_interval: int

    def apply_effect(self) -> None:
        self.character.take_damage(self.damage_per_interval)


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

    # Add a non-refresh effect and return its generated key.
    # The caller retains that key. If no_refresh_req_is_timed is set, effect
    # will be automatically be pruned at end of timer.
    # else it is creator's job to call remove_effect_by_key() when the effect should end.
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
    # this per frame; non-refresh effects must use add_non_refresh_effect() instead.
    def refresh_effects_requiring_refresh(self, effects: Sequence[TimedCharacterEffect]) -> None:
        for effect in effects:

            if effect.requires_refresh == False:
                raise ValueError(
                    "refresh_effects_requiring_refresh can only be sent "
                    f"refresh-required effects, received {effect}"
                )
        
            pre_existing = self._find_effect_by_key(effect.effect_key)

            # if it's already in the tracked list, flip if it was residual 
            if pre_existing is not None:
                if pre_existing.state == RefreshRequiredTimedEffectState.RESIDUAL:
                    pre_existing.reactivate_from_residual()
            else:
                # if it's not already in the list, add it for processing
                self.tracked_timed_effects.append(effect)

            # in all cases mark that we saw it
            self._refreshed_effect_keys_this_frame.add(effect.effect_key)

    # Once per frame, move absent refresh-required effects into residual or remove
    # them, advance every remaining effect, then prune expired residual and
    # automatically expiring non-refresh effects.
    def process(self, delta_secs: float) -> None:

        prune_key_set = set()

        # Refresh-required effects absent from every refresh source this frame either enter
        # residual or end immediately.
        for effect in self.tracked_timed_effects:
            if (effect.effect_key not in self._refreshed_effect_keys_this_frame
                    and effect.requires_refresh is True):
                if effect.state == RefreshRequiredTimedEffectState.ACTIVE:
                        # residual_secs_base > 0 indicates effect has a defined residual phase
                        # (which we should enter)
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

        # Update all remaining effects and collect residual or automatic timers that expired.
        for effect in self.tracked_timed_effects:
            effect.update(delta_secs)

            if effect.state == RefreshRequiredTimedEffectState.RESIDUAL and effect.residual_secs_left <= 0:
                prune_key_set.add(effect.effect_key)
            elif (effect.requires_refresh is False and
                  effect.no_refresh_req_is_timed is True and
                  effect.no_refresh_req_timer_secs_left <= 0):
                prune_key_set.add(effect.effect_key)

        # Prune effects whose timers have expired.
        if prune_key_set:
            self.tracked_timed_effects = [effect
                                          for effect in self.tracked_timed_effects
                                          if effect.effect_key not in prune_key_set]












