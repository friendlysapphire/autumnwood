from dataclasses import dataclass, field
from enum import StrEnum
import pygame

# Define the gameplay meanings used by rectangular regions loaded from Tiled.
# String values must match the region_type values authored in the map.
class RegionType(StrEnum):
    SOLID = "solid"
    NAVIGABLE_DEEP_WATER = "nav_deep_water"
    NAVIGABLE_SHALLOW_WATER = "nav_shallow_water"
    MAP_TRANSITION = "map_transition"

@dataclass(kw_only=True)
class Region:
    rect: pygame.Rect 
    type: RegionType

    # Return whether this region can be entered under ordinary movement rules,
    # ignoring temporary abilities, equipment, vehicles, keys, or other overrides
    def is_walkable_by_default(self) -> bool:
        match self.type:
            case RegionType.SOLID | RegionType.NAVIGABLE_DEEP_WATER:
                return False
            case RegionType.NAVIGABLE_SHALLOW_WATER | RegionType.MAP_TRANSITION:
                return True
            case _:
                raise ValueError(f"Region type {self.type} needs defined walkable_by_default behavior.")


# A transition region carries the destination needed to move the player to another map.
# Its RegionType is fixed automatically so callers cannot create an inconsistent transition.
@dataclass(kw_only=True)
class MapTransitionRegion(Region):
    destination_map: str
    destination_spawn: str
    type: RegionType = field(init=False, default=RegionType.MAP_TRANSITION)