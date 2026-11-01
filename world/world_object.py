from dataclasses import dataclass, field
from enum import StrEnum

import pygame

# Define the gameplay meanings used by rectangular world-object hitboxes loaded from Tiled.
# String values must match the world_object_type values authored in the map.
class WorldObjectType(StrEnum):
    APPLE_TREE = "apple_tree"


# WorldObject is an invisible gameplay representation that can remain separate from
# its visible scenery art.
@dataclass(kw_only=True)
class WorldObject:
    rect: pygame.Rect 
    type: WorldObjectType
    name: str = "generic" 


# AppleTree fixes its type so callers cannot construct an inconsistent AppleTree.
@dataclass(kw_only=True)
class AppleTree(WorldObject):
    type: WorldObjectType = field(init=False, default=WorldObjectType.APPLE_TREE)
   
    _num_apples: int = 10

    def pick_apple(self) -> tuple[bool, str]:
        if self._num_apples > 0:
            self._num_apples -= 1
            return (True, "You pick an apple.")
        else:
            return(False, "This apple tree has no apples to pick.")

    def has_apples_to_pick(self) -> bool:
        return self._num_apples > 0

    def return_apple(self, num: int = 1) -> int:
        self._num_apples += num

    @property
    def num_apples(self) -> int:
        return self._num_apples
        



