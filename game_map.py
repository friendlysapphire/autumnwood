from pathlib import Path

import pygame
import pytmx
from pytmx.util_pygame import load_pygame

from character import Character
from region import MapTransitionRegion, QuicksandRegion, Region, RegionType
from region_effects import ActiveRegionEffects, MapTransitionRegionEffect, SpeedRegionEffect
from world_object import AppleTree, WorldObject, WorldObjectType


QUICKSAND_PERCENT_CHANGE = -0.50

class GameMap:

    def __init__(self, map_path: Path) -> None:

        # Load the Tiled map and its referenced tile images.
        self.tiled_map = load_pygame(map_path)

        # Load the gameplay regions defined by the map.
        self.regions, self.world_objects = self._load_map_regions_and_world_objects()

        # Convert the map dimensions from tiles into world pixels.
        self.height = self.tiled_map.height * self.tiled_map.tileheight
        self.width = self.tiled_map.width * self.tiled_map.tilewidth

    # Find the requested named spawn point in Tiled and return its world coordinates.
    def get_spawn_coords(self,
                               spawn_name: str
                               ) -> tuple[float, float]:

        for layer in self.tiled_map.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                if layer.name == "Spawns":
                    for obj in layer:
                        if obj.name == spawn_name:
                            return (obj.x, obj.y)

        raise ValueError(f"Could not find player spawn location {spawn_name} for {self.tiled_map.filename}.")

    # Return every gameplay region currently intersecting the player's collision rectangle.
    def get_regions_intersecting_character(self,
                                           character: Character
                                           ) -> tuple[Region, ...]:

        char_collision_rect = character.get_collision_rect()

        intersecting_regions = (
            region
            for region in self.regions
            if char_collision_rect.colliderect(region.rect)
            )
    
        return tuple(intersecting_regions)

    # return every world object intersecting with the character's current position
    def get_world_objs_intersecting_character(self,
                                              character: Character
                                              ) -> tuple[WorldObject, ...]:
        
        char_collision_rect = character.get_collision_rect()

        intersecting_wobjs = (
            wobj
            for wobj in self.world_objects
            if char_collision_rect.colliderect(wobj.rect)
            )

        return tuple(intersecting_wobjs)

    # INTERNAL ONLY METHODS

    # Load gameplay regions & world objects from Tiled.
    # Collision-layer objects are always SOLID; Regions-layer objects define their type explicitly.)
    def _load_map_regions_and_world_objects(self) -> tuple[tuple[Region, ...], tuple[WorldObject, ...]]:

        region_list: list[Region] = []
        world_obj_list: list[WorldObject] = []

        for layer in self.tiled_map.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                #todo switch to match here
                if layer.name == "Collisions":
                    for obj in layer:
                        crect: pygame.Rect = pygame.Rect(obj.x, 
                                                        obj.y, 
                                                        obj.width, 
                                                        obj.height)
                        
                        region_list.append(Region(rect=crect, type=RegionType.SOLID))

                if layer.name == "World Objects":
                    for obj in layer:
                        world_obj_rect = pygame.Rect(obj.x,
                                                obj.y,
                                                obj.width,
                                                obj.height)
                        
                        obj_type = obj.properties.get("world_object_type")

                        if obj_type == WorldObjectType.APPLE_TREE:
                            world_obj = AppleTree(rect=world_obj_rect,
                                                name=obj.name)

                            world_obj_list.append(world_obj)
                        else:
                            raise KeyError(
                                f"World Object at ({obj.x}, {obj.y}) needs a recognized "
                                f"world_object_type: {obj.properties}"
                            )

                if layer.name == "Regions":
                    for obj in layer:
                        region_rect = pygame.Rect(obj.x,
                                                obj.y,
                                                obj.width,
                                                obj.height)

                        r_type = obj.properties.get("region_type")

                        if r_type == RegionType.MAP_TRANSITION:

                            try:
                                r_dest_map = obj.properties["destination_map"]
                                r_dest_spawn = obj.properties["destination_spawn"]
                            except KeyError as e:
                                raise KeyError(
                                    f"MapTransition object missing destination_map or "
                                    f"destination_spawn at ({obj.x}, {obj.y}): {obj.properties}"
                                    ) from e

                            region_list.append(MapTransitionRegion(rect=region_rect,
                                                                destination_map=r_dest_map,
                                                                destination_spawn=r_dest_spawn)) 
                        elif r_type == RegionType.QUICKSAND:
                            region_list.append(QuicksandRegion(rect=region_rect,
                                                            percent_change=QUICKSAND_PERCENT_CHANGE))  
                        # Region types that need no additional runtime data can use the base Region class.
                        elif r_type:
                            region_list.append(Region(rect=region_rect, type=RegionType(r_type)))
                        else:
                            raise KeyError(
                                f"All objects in Regions layer need region_type: {obj.x}: {obj.y} : {obj.properties}")

                            
        return tuple(region_list), tuple(world_obj_list)
