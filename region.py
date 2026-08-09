from dataclasses import dataclass
from enum import StrEnum
import pygame

# Define the gameplay meaning of rectangular regions loaded from Tiled.
class RegionType(StrEnum):
    SOLID = "solid"
    NAVIGABLE_DEEP_WATER = "nav_deep_water"
    NAVIGABLE_SHALLOW_WATER = "nav_shallow_water"

@dataclass
class Region:
    rect: pygame.Rect 
    type: RegionType

    # Return whether this region can be entered under ordinary movement rules,
    # ignoring temporary abilities, equipment, vehicles, keys, or other overrides
    def is_walkable_by_default(self) -> bool:
        match self.type:
            case RegionType.SOLID | RegionType.NAVIGABLE_DEEP_WATER:
                return False
            case RegionType.NAVIGABLE_SHALLOW_WATER:
                return True
            case _:
                raise ValueError(f"Region type {self.type} needs defined walkable_by_default behavior.")

