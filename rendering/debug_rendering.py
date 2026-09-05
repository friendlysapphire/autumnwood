
import pygame      

from characters.character import Character
from world.game_map import GameMap 
from world.region import RegionType

# Draw runtime regions and hitboxes over the completed scene for diagnosis only.
def draw_debug_overlays(*,
                        screen: pygame.Surface,
                        current_map: GameMap,
                        player: Character,
                        camera_x: int,
                        camera_y: int
                        ) -> None:

    # Rect.move() (used below) adds its offset, so use the negative camera position to perform
    # the same world-to-screen translation as world_position - camera_position.
    camera_screen_offset_x = round(-camera_x)
    camera_screen_offset_y = round(-camera_y)

    # Shift each region rectangle into screen coordinates for debug drawing.
    for region in current_map.regions:
        region_rect = region.rect

        match region.type:
            case RegionType.SOLID:
                debug_rect_color = "darkorange"
            case RegionType.NAVIGABLE_DEEP_WATER:
                debug_rect_color = "cornsilk"
            case RegionType.NAVIGABLE_SHALLOW_WATER:
                debug_rect_color = "coral2"
            case RegionType.MAP_TRANSITION:
                debug_rect_color = "deeppink1"
            case RegionType.QUICKSAND:
                debug_rect_color = "goldenrod3"
            case _:
                debug_rect_color = "chocolate4"

        camera_adjusted_rect = region_rect.move(camera_screen_offset_x, camera_screen_offset_y)
        pygame.draw.rect(screen, debug_rect_color, camera_adjusted_rect, width=2)

    for world_object in current_map.world_objects:
        world_obj_rect = world_object.rect
        camera_adjusted_rect = world_obj_rect.move(camera_screen_offset_x, camera_screen_offset_y)
        pygame.draw.rect(screen, "mediumseagreen", camera_adjusted_rect, width=2)
    
    for npc in current_map.npcs:
        npc_rect = npc.interaction_rect
        camera_adjusted_rect = npc_rect.move(camera_screen_offset_x, camera_screen_offset_y)
        pygame.draw.rect(screen, "gold4", camera_adjusted_rect, width=2)
        
    # Shift the player's collision rectangle into screen coordinates for debug drawing.
    base_player_crect = player.get_collision_rect()
    camera_adjusted_rect = base_player_crect.move(camera_screen_offset_x, camera_screen_offset_y)
    pygame.draw.rect(screen, pygame.Color('darkorchid1'), camera_adjusted_rect, width=2)
