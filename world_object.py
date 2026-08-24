from dataclasses import dataclass, field
from enum import StrEnum
import pygame

# Define the gameplay meanings used by rectangular regions loaded from Tiled.
# String values must match the world_object_type values authored in the map.
class WorldObjectType(StrEnum):
    APPLE_TREE = "apple_tree"


@dataclass(kw_only=True)
class WorldObject:
    rect: pygame.Rect 
    type: WorldObjectType
    name: str | None = None

# A transition region carries the destination needed to move the player to another map.
# Its RegionType is fixed automatically so callers cannot create an inconsistent transition.
@dataclass(kw_only=True)
class AppleTree(WorldObject):
    type: WorldObjectType = field(init=False, default=WorldObjectType.APPLE_TREE)


