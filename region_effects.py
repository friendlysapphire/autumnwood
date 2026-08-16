from dataclasses import dataclass

# Collect the region-derived effects that apply to the player at the current position.
@dataclass(kw_only=True)
class RegionEffects:
    map_transition_effect: MapTransitionRegionEffect | None = None
    speed_effect_list: tuple[SpeedRegionEffect, ...] | None = ()

# Describe a requested transition to a named spawn in another map.
@dataclass(kw_only=True)
class MapTransitionRegionEffect:
    destination_map: str
    destination_spawn: str

# Describe a temporary percentage change to movement speed.
@dataclass(kw_only=True)
class SpeedRegionEffect:
    percent_change: float

