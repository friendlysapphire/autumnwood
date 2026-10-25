from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum

from characters.character import Character

# ACTIVE effects are currently supplied by a source; RESIDUAL effects keep applying
# temporarily after their source stops supplying them.
class TimedEffectState(Enum):
    ACTIVE = 0
    RESIDUAL = 1

# Base class for an effect that persists across frames and owns its own tick/residual timers.
# The processor tracks these instances and decides when their source has appeared or disappeared.
@dataclass(kw_only=True)
class TimedCharacterEffect(ABC):
    character: Character

    # Identifies one ongoing effect for processor tracking. Matching keys refresh an existing
    # effect rather than starting a duplicate timer.
    effect_key: str
    tick_interval_secs: float

    state: TimedEffectState = TimedEffectState.ACTIVE
    
    residual_secs_base: float = 0.0

    # Effects supplied by regions are refreshed every frame. Persistent effects can opt out
    # and remain tracked until a future system explicitly removes them.
    requires_refresh: bool = True

    # Runtime counters belong to this persistent effect instance, not to the fresh effect
    # descriptions supplied by regions each frame.
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
        self.state = TimedEffectState.RESIDUAL

        #reset all internal timers
        self.residual_secs_left = self.residual_secs_base
        self.interval_elapsed_secs = 0

# Timed effect that repeatedly applies absolute health damage while active or residual.
@dataclass(kw_only=True)
class TimedDamageEffectAbs(TimedCharacterEffect):

    damage_per_interval: int

    def update(self, delta_secs: float) -> None:
        secs_since_last_trigger = self.interval_elapsed_secs + delta_secs

        if self.state == TimedEffectState.RESIDUAL:
            self.residual_secs_left -= delta_secs
            if self.residual_secs_left <= 0:
                # TODO: seems like there are some cases where we'd want to apply one more take_damage() but I don't
                # feel like thinking about that at the moment. worst case off by 1 frame.
                return
        
        if secs_since_last_trigger >= self.tick_interval_secs:
            self.interval_elapsed_secs = secs_since_last_trigger - self.tick_interval_secs
            self.character.take_damage(self.damage_per_interval)
        else:
            self.interval_elapsed_secs = secs_since_last_trigger


# Tracks timed-effect instances across frames. Sources may refresh effects several times
# per frame; the game loop calls process() once after all sources have reported.
class TimedCharacterEffectProcessor:

    def __init__(self):
        self.tracked_timed_effects: list[TimedCharacterEffect] = []
        self._refreshed_effect_keys_this_frame: set[str] = set()

    def _find_effect_by_key(self, in_key: str) -> TimedCharacterEffect | None:
        return next((x for x in self.tracked_timed_effects if x.effect_key == in_key), None)

    # Record effects currently supplied by one source. This may be called multiple times per
    # frame before process() decides which tracked effects were not refreshed.
    def refresh_effects(self, effects: Sequence[TimedCharacterEffect]) -> None:
        for effect in effects:
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

        prune_set = set()

        # first pass prune -- events we didn't see in a refresh this time through
        for effect in self.tracked_timed_effects:
            if (effect.effect_key not in self._refreshed_effect_keys_this_frame
                    and effect.requires_refresh is True):
                if effect.state == TimedEffectState.ACTIVE:
                        if effect.residual_secs_base > 0:
                            effect.enter_residual_phase()
                        else:
                            prune_set.add(effect.effect_key)

        for key in prune_set:
            # this can't be the most efficient way to do this but these lists are going to be small
            self.tracked_timed_effects = [x 
                                          for x in self.tracked_timed_effects 
                                          if x.effect_key != key]

        self._refreshed_effect_keys_this_frame.clear()
        prune_set.clear()

        # update all remaining items and generate second prune list (effects in residual phase that have expired)
        for effect in self.tracked_timed_effects:
            effect.update(delta_secs)

            if effect.state == TimedEffectState.RESIDUAL and effect.residual_secs_left <= 0:
                prune_set.add(effect.effect_key)

        # prune effects in residual phase that have timed out
        for key in prune_set:
            # this can't be the most efficient way to do this but these lists are going to be small
            self.tracked_timed_effects = [x 
                                          for x in self.tracked_timed_effects 
                                          if x.effect_key != key]











