from pathlib import Path
from player import Player, DirectionValue

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

    player = Player(name="Elf Mage",
                    sprite_path=MAIN_CHAR_FILE_PATH,
                    spawn_offset_x=PLAYER_X_OFFSET,
                    spawn_offset_y=PLAYER_Y_OFFSET,
                    collision_offset_x=PLAYER_X_COLLISION_ADJ,
                    collision_offset_y=PLAYER_Y_COLLISION_ADJ,
                    collision_box_height=PLAYER_COLLISION_HEIGHT,
                    collision_box_width=PLAYER_COLLISION_WIDTH,
                    default_speed=PLAYER_SPEED)
    
    player.spawn(spawn_x, spawn_y)

    # get all the collision rects for our map
    col_rect_list: list[pygame.Rect] = get_collision_rects(tiled_map)

    # where player would be with movement based on keypress. used to check for collisions or 
    # other events before updating (and allowing player to move)
    player_x_new: float = 0
    player_y_new: float = 0
    move_attempt_x: bool = False
    move_attempt_y: bool = False

    running = True

    while running:

        # clear movement from last frame. +1, 0, or -1. 
        player.direction_x  = 0
        player.direction_y = 0
        
        # clear flag showing attempted movement in this frame
        move_attempt_x = False
        move_attempt_y = False

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
            player.direction_x = -1
            move_attempt_x = True
        elif pressed_keys[pygame.K_RIGHT]:
            player.direction_x = 1
            move_attempt_x = True
        if pressed_keys[pygame.K_UP]:
            player.direction_y = -1
            move_attempt_y = True
        elif pressed_keys[pygame.K_DOWN]:
            player.direction_y = 1
            move_attempt_y = True
        
        # if they're trying to move, calculate where that would move them to and if that would be a collision
        # before allowing the change
        if move_attempt_x or move_attempt_y:
            player_x_new = player.world_x + (player.direction_x * player.speed * delta_secs)
            player_y_new = player.world_y + (player.direction_y * player.speed * delta_secs)

            # see if the new player location would be a collision, if so, keep old player location
            # use the adjustment factors so we're using a small rect around the feet only
            proposed_pos_rect = player.get_collision_rect(player_x_new, player_y_new)
            
            # if no collision, intended new place becomes current place
            if proposed_pos_rect.collidelist(col_rect_list) == -1:
                player.world_x = player_x_new
                player.world_y = player_y_new
            elif move_attempt_x and move_attempt_y:
                # player is trying to move diagonally, see if one of those directions is ok
                # and if so, move in the allowable direction.
                # both might fail or max one of them might be ok
                
                # test x movement
                proposed_pos_rect = player.get_collision_rect(player_x_new, player.world_y)

                # if we can move in the x direction, set the new x position
                if proposed_pos_rect.collidelist(col_rect_list) == -1:
                    player.world_x = player_x_new
                else:
                    # if we can't move in the X direction, test Y and update accordingly
                    proposed_pos_rect = player.get_collision_rect(player.world_x, player_y_new)

                    if proposed_pos_rect.collidelist(col_rect_list) == -1:
                        player.world_y = player_y_new

        # Draw each visible tile layer from bottom to top.
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for tile_x, tile_y, tile_image in layer.tiles():
                    screen_x = tile_x * tiled_map.tilewidth
                    screen_y = tile_y * tiled_map.tileheight

                    screen.blit(tile_image, (screen_x, screen_y))
        
        screen.blit(player.sprite,(player.world_x, player.world_y))

        # Make the completed frame visible
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()