from collections.abc import Sequence
from dataclasses import dataclass, field

from region import MapTransitionRegion, QuicksandRegion, Region

# Shared base type lets ActiveRegionEffects group different effect descriptions together.
@dataclass
class RegionEffect:
    pass

# Group the region-derived effects that apply at one position by when they are processed.
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

# Translate already-intersecting regions into effect descriptions. This function neither
# finds intersections nor applies effects, keeping it independent of GameMap and Character.
def get_active_region_effects(intersecting_regions: Sequence[Region]) -> ActiveRegionEffects:

    region_effects = ActiveRegionEffects()

    for region in intersecting_regions:

        if isinstance(region, MapTransitionRegion):

            effect = MapTransitionRegionEffect(destination_map=region.destination_map,
                                            destination_spawn=region.destination_spawn)
            region_effects.post_move_effects.append(effect)

        elif isinstance(region,QuicksandRegion):
            effect = SpeedRegionEffect(percent_change=region.percent_change)
            region_effects.pre_move_effects.append(effect)

    return region_effects
