from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum

from characters.character import Character

class TimedEffectState(Enum):
    ACTIVE = 0
    RESIDUAL = 1

@dataclass(kw_only=True)
class TimedCharacterEffect(ABC):
    character: Character

    effect_key: str
    tick_interval_secs: float

    state: TimedEffectState = TimedEffectState.ACTIVE
    
    residual_secs_base: float = 0.0

    # v2 support for timed effects that don't need to be refreshed every time through the main loop
    # will also need a unique key or something as well, but this is the start at least
    requires_refresh: bool = True

    # Runtime counters are created by the class
    residual_secs_left: float = field(init=False)
    interval_elapsed_secs: float = field(init=False)

    @abstractmethod
    def update(self, delta_secs: float):
        pass

    def __post_init__(self):
        self.residual_secs_left = self.residual_secs_base
        self.interval_elapsed_secs = 0

@dataclass(kw_only=True)
class TimedDamageEffectAbs(TimedCharacterEffect):

    damage_per_interval: int

    def update(self, delta_secs: float) -> None:
        secs_since_last_trigger = self.interval_elapsed_secs + delta_secs

        if self.state == TimedEffectState.RESIDUAL:
            self.residual_secs_left -= delta_secs
            if self.residual_secs_left <= 0:
                return
        
        if secs_since_last_trigger >= self.tick_interval_secs:
            self.interval_elapsed_secs = secs_since_last_trigger - self.tick_interval_secs
            self.character.take_damage(self.damage_per_interval)
        else:
            self.interval_elapsed_secs = secs_since_last_trigger

class TimedCharacterEffectProcessor:

    def __init__(self, player: Character):
        self.player = player
        self.timed_effects: list[TimedCharacterEffect] = []


