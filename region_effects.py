from dataclasses import dataclass, field

@dataclass
class RegionEffect:
    pass

# Collect the region-derived effects that apply to the player at the current position.
@dataclass(kw_only=True)
class ActiveRegionEffects:
    pre_move_effects: list[RegionEffect] = field(default_factory=list)
    post_move_effects: list[RegionEffect] = field(default_factory=list)


### PRE-MOVE EFFECTS

# Describe a temporary percentage change to movement speed.
@dataclass(kw_only=True)
class SpeedRegionEffect(RegionEffect):
    percent_change: float

### POST-MOVE EFFECTS

# Describe a requested transition to a named spawn in another map.
@dataclass(kw_only=True)
class MapTransitionRegionEffect(RegionEffect):
    destination_map: str
    destination_spawn: str


