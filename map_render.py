import pygame      
import pytmx 

from game_map import GameMap 

     
# Draw each visible tile layer from bottom to top.
def draw_map(screen: pygame.Surface,
             current_map: GameMap,
             camera_x: int,
             camera_y: int
             ) -> None:
    
    # Tiled supplies tile coordinates; convert them to world pixels, then subtract the
    # camera's world position to place each tile in the screen view.
    for layer in current_map.tiled_map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for tile_x, tile_y, tile_image in layer.tiles():
                tile_world_x = tile_x * current_map.tiled_map.tilewidth
                tile_world_y = tile_y * current_map.tiled_map.tileheight
                tile_screen_x = round(tile_world_x - camera_x)
                tile_screen_y = round(tile_world_y - camera_y)

                screen.blit(tile_image, (tile_screen_x, tile_screen_y))
