import pygame      
import pytmx 

from game_map import GameMap 

     
# Draw each visible tile layer from bottom to top.
def draw_map(screen: pygame.Surface,
             current_map: GameMap,
             camera_x: int,
             camera_y: int
             ) -> None:
    
    for layer in current_map.tiled_map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for tile_x, tile_y, tile_image in layer.tiles():
                tile_world_x = tile_x * current_map.tiled_map.tilewidth
                tile_world_y = tile_y * current_map.tiled_map.tileheight
                tile_screen_x = round(tile_world_x - camera_x)
                tile_screen_y = round(tile_world_y - camera_y)

                # Convert the tile's world position to its position inside the camera view.
                screen.blit(tile_image, (tile_screen_x, tile_screen_y))