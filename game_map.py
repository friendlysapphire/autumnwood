from pathlib import Path

import pygame
import pytmx
from pytmx.util_pygame import load_pygame

from character import Character
from character_scaffolds import TRAVELING_VENDOR
from npcs import NPC, NPCType
from region import MapTransitionRegion, QuicksandRegion, Region, RegionType
from world_object import AppleTree, WorldObject, WorldObjectType


QUICKSAND_PERCENT_CHANGE = -0.50

# GameMap turns Tiled's authored map metadata into runtime map objects and answers
# spatial questions about them. It does not apply the gameplay effects those objects imply.
class GameMap:

    def __init__(self, map_path: Path) -> None:

        # Load the Tiled map and its referenced tile images.
        self.tiled_map = load_pygame(map_path)

        # Convert the map's authored gameplay elements into their runtime representations.
        self.regions, self.world_objects, self.npcs = self._load_map_elements()

        # Convert the map dimensions from tiles into world pixels.
        self.height = self.tiled_map.height * self.tiled_map.tileheight
        self.width = self.tiled_map.width * self.tiled_map.tilewidth


    # Find the requested named spawn point in Tiled and return its world coordinates.
    def get_player_spawn_coords(self,
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

    # Return every world object intersecting the character's feet collision rectangle.
    # WorldObject.rect is an invisible gameplay hitbox, separate from its scenery art.
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

    # Load gameplay regions, world objects, and NPCs from Tiled.
    # Collisions become ordinary SOLID Regions; special Regions and World Objects become
    # specialized runtime objects only when their authored data requires it.
    def _load_map_elements(self) -> tuple[tuple[Region, ...], tuple[WorldObject, ...], list[NPC]]:

        region_list: list[Region] = []
        world_obj_list: list[WorldObject] = []
        npcs_list: list[NPC] = []

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
                if layer.name == "NPCs":
                    for obj in layer:

                        # NPC point objects provide a runtime character type and its initial
                        # feet-center placement. Delayed NPCs opt out of only the map-load spawn.
                        npc_type = obj.properties.get("character_type")

                        spawn_on_map_load = obj.properties.get("spawn_on_map_load", True)
  

                        match npc_type:

                            case NPCType.TRAVELING_VENDOR:
                                # Map the authored type to the scaffold that defines this NPC's
                                # visual and collision configuration.
                                vendor1 = NPC(name=obj.name,
                                              scaffold=TRAVELING_VENDOR,
                                              npc_type=NPCType.TRAVELING_VENDOR,
                                              spawn_on_map_load=spawn_on_map_load,
                                              initial_x_spawn=obj.x,
                                              initial_y_spawn=obj.y)
                                
                                npcs_list.append(vendor1)
                                print(obj.properties)

                            case _:
                                raise KeyError(
                                f"NPC object at ({obj.x}, {obj.y}) needs a recognized "
                                f"character_type: {obj.properties} from NPCType"
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

        # NPCs are mutable map runtime state: they may move, be removed, or appear later.
        # Regions and current world objects remain fixed-size map-derived collections for now.
        return tuple(region_list), tuple(world_obj_list), npcs_list
    
