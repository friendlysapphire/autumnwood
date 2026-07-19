from pathlib import Path

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAP_PATH = PROJECT_ROOT / "resources" / "testmap.tmx"

# playr speed is in pixels per second
PLAYER_SPEED = 120

# Pygame draws from the image's top-left, we want to be centered aroound the feet. w/o this adjustment
# char would appear in world down and to right of where the spawn point visually appears on the map.
PLAYER_X_OFFSET = 32
PLAYER_Y_OFFSET = 52

# collision based on small rect around the feet, not whole sprite
PLAYER_X_COLLISION_ADJ = 24
PLAYER_Y_COLLISION_ADJ = 46
PLAYER_COLLISION_WIDTH = 16
PLAYER_COLLISION_HEIGHT = 10

MAIN_CHAR_FILE_PATH = (
    PROJECT_ROOT
    / "resources"
    / "PixelWorldSprites"
    / "UnitsSprites"
    / "Units"
    / "ElfMage_64.png"
)

def get_collision_rects(tiled_map: pytmx.TiledMap) -> list[pygame.Rect]:

    col_list: list[pygame.Rect] = []

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Collisions":
                for obj in layer:
                    crect: pygame.Rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    col_list.append(crect)
    
    return col_list

def get_player_start(tiled_map: pytmx.TiledMap) -> tuple[float, float]:

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Spawns":
                for obj in layer:
                    if obj.name == "player_start":
                        return (obj.x, obj.y)

    raise ValueError("Could not find initial player start location.")

def main() -> None:
    # Set up Pygame and create the game window.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Xiao map test")
    clock = pygame.time.Clock()

    # Load the Tiled map and its referenced tile images.
    tiled_map = load_pygame(MAP_PATH)

    # get player start location
    spawn_x, spawn_y = get_player_start(tiled_map)


    # The spawn point is where we want the character centered at the feet.
    # Shift the sprite up and left because Pygame draws images from their top-left corner.
    player_x = spawn_x - PLAYER_X_OFFSET
    player_y = spawn_y - PLAYER_Y_OFFSET

    # get all the collision rects for our map
    col_rect_list: list[pygame.Rect] = get_collision_rects(tiled_map)

    player_sprite_sheet = pygame.image.load(MAIN_CHAR_FILE_PATH)
    player_sprite_sheet = player_sprite_sheet.convert_alpha()
    sprite_rect = pygame.Rect(0, 0, 64, 64) 
    player_sprite = player_sprite_sheet.subsurface(sprite_rect)

    # direction player is moving
    direction_x: int = 0
    direction_y: int = 0

    # where player would be with movement based on keypress. used to check for collisions or 
    # other events before updating (and allowing player to move)
    player_x_new: float = 0
    player_y_new: float = 0
    move_attempt: bool = False

    running = True

    while running:

        # clear movement from last frame
        direction_x  = 0
        direction_y = 0
        
        # clear flag showing attempted movement in this frame
        move_attempt = False

        elapsed_ms = clock.tick(FRAMES_PER_SECOND)
        delta_secs = elapsed_ms / 1000
        
        # Read pending window and input events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the previous frame before drawing the map again.
        screen.fill("black")

        # get keypresses for player movement, set direction
        pressed_keys = pygame.key.get_pressed()
       
        if pressed_keys[pygame.K_LEFT]:
            direction_x = -1
            move_attempt = True
        elif pressed_keys[pygame.K_RIGHT]:
            direction_x = 1
            move_attempt = True
        if pressed_keys[pygame.K_UP]:
            direction_y = -1
            move_attempt = True
        elif pressed_keys[pygame.K_DOWN]:
            direction_y = 1
            move_attempt = True
        
        # if they're trying to move, calculate where that would move them to and if that would be a collision
        # before allowing the change
        if move_attempt:
            player_x_new = player_x + (direction_x * PLAYER_SPEED * delta_secs)
            player_y_new = player_y + (direction_y * PLAYER_SPEED * delta_secs)

            # see if the new player location would be a collision, if so, keep old player location
            # use the adjustment factors so we're using a small rect around the feet only
            proposed_pos_rect = pygame.Rect(player_x_new + PLAYER_X_COLLISION_ADJ, 
                                            player_y_new + PLAYER_Y_COLLISION_ADJ, 
                                            PLAYER_COLLISION_WIDTH,
                                            PLAYER_COLLISION_HEIGHT)
            
            # if no collision, intended new place becomes current place
            if proposed_pos_rect.collidelist(col_rect_list) == -1:
                player_x = player_x_new
                player_y = player_y_new

        # Draw each visible tile layer from bottom to top.
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for tile_x, tile_y, tile_image in layer.tiles():
                    screen_x = tile_x * tiled_map.tilewidth
                    screen_y = tile_y * tiled_map.tileheight

                    screen.blit(tile_image, (screen_x, screen_y))
        
        screen.blit(player_sprite,(player_x, player_y))

        # Make the completed frame visible
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()