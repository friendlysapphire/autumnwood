from collections.abc import Sequence
from dataclasses import dataclass, field

from characters.character import Character
from characters.timed_effects import TimedCharacterEffect, TimedDamageEffectAbs
from world.region import MapTransitionRegion, QuicksandRegion, Region, PoisonCloudRegion

# Shared base type for immediate region actions used before or after movement. Timed
# character effects are kept separately because they use their own cross-frame lifecycle.
@dataclass
class RegionEffect:
    pass

# Group the effects discovered from one set of intersecting regions.
# get_active_region_effects() creates and populates this result for the game loop to consume.
@dataclass(kw_only=True)
class ActiveRegionEffects:
    pre_move_effects: list[RegionEffect] = field(default_factory=list)
    post_move_effects: list[RegionEffect] = field(default_factory=list)
    # Generic timed effects currently supplied by intersecting regions. The timed-effect
    # processor retains matching effects and their timer state across frames.
    timed_character_effects: list[TimedCharacterEffect] = field(default_factory=list)

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

# GameMap turns Tiled-authored rectangles into Region subclasses; this function turns the
# currently intersecting runtime regions into their current gameplay-effect descriptions.
# It neither finds intersections nor applies effects. character binds timed effects to the
# target they will eventually update.
def get_active_region_effects(character: Character, intersecting_regions: Sequence[Region]) -> ActiveRegionEffects:

    region_effects = ActiveRegionEffects()

    for region in intersecting_regions:

        if isinstance(region, MapTransitionRegion):

            effect = MapTransitionRegionEffect(destination_map=region.destination_map,
                                            destination_spawn=region.destination_spawn)
            region_effects.post_move_effects.append(effect)

        elif isinstance(region,QuicksandRegion):
            effect = SpeedRegionEffect(percent_change=region.percent_change)
            region_effects.pre_move_effects.append(effect)

        elif isinstance(region,PoisonCloudRegion):
            # Region discovery creates a fresh description each frame. The timed-effect processor
            # recognizes this key and retains the persistent effect instance that owns its timers.
            effect = TimedDamageEffectAbs(character=character,
                                          effect_key="poison cloud",
                                          damage_per_interval=region.damage_amount,
                                          tick_interval_secs=region.damage_interval_secs,
                                          residual_secs_base=region.residual_secs
                                          )

            region_effects.timed_character_effects.append(effect)

    return region_effects
