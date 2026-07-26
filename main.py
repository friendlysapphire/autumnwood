from pathlib import Path
from character import Character

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640

FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAP_PATH = PROJECT_ROOT / "resources" / "testmap.tmx"


# Elf Mage player construction details
# player speed is in pixels per second
ELF_MAGE_PLAYER_SPEED = 120

# Pygame draws from the image's top-left, we want to be centered aroound the feet. w/o this adjustment
# char would appear in world down and to right of where the spawn point visually appears on the map.
ELF_MAGE_SPAWN_OFFSET_X = 32
ELF_MAGE_SPAWN_OFFSET_Y = 52

# collision based on small rect around the feet, not whole sprite. defines a rect inside the sprite image
# x and y are the top-left coord
ELF_MAGE_COLLISION_RECT_X = 23
ELF_MAGE_COLLISION_RECT_Y = 44
ELF_MAGE_COLLISION_RECT_WIDTH = 18
ELF_MAGE_COLLISION_RECT_HEIGHT = 6

# lines in from edges of sprite image the charater (walking sprite) begins as solid. useful for drawing 
# up to edge of window correctly. 
ELF_MAGE_VISIBLE_TOP_OFFSET = 12
ELF_MAGE_VISIBLE_BOTTOM_OFFSET = 15
ELF_MAGE_VISIBLE_LEFT_OFFSET = 19
ELF_MAGE_VISIBLE_RIGHT_OFFSET = 16

ELF_MAGE_FILE_PATH = (
    PROJECT_ROOT
    / "resources"
    / "PixelWorldSprites"
    / "UnitsSprites"
    / "Units"
    / "ElfMage_64.png"
)

# Read the rectangular collision objects from Tiled's Collisions layer
# and convert them into Pygame rectangles.
def get_collision_rects(tiled_map: pytmx.TiledMap) -> list[pygame.Rect]:

    col_list: list[pygame.Rect] = []

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Collisions":
                for obj in layer:
                    crect: pygame.Rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    col_list.append(crect)
    
    return col_list

# Find the named player spawn point in Tiled and return its world coordinates.
def get_player_start(tiled_map: pytmx.TiledMap) -> tuple[float, float]:

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Spawns":
                for obj in layer:
                    if obj.name == "player_start":
                        return (obj.x, obj.y)

    raise ValueError("Could not find initial player start location.")

# A proposed position is valid only if the character stays within the map
# and its collision rectangle does not overlap a map obstacle.
def is_proposed_player_move_valid(proposed_x: float, 
                                  proposed_y: float, 
                                  char: Character, 
                                  map_collision_rects: list[pygame.Rect],
                                  map_width: int,
                                  map_height: int
                                  ) -> bool:
    
    in_bounds = char.is_within_bounds(proposed_x, proposed_y, x_size=map_width, y_size=map_height)

    player_collision_rect = char.get_collision_rect(proposed_x, proposed_y)
    no_collision = player_collision_rect.collidelist(map_collision_rects) == -1

    return in_bounds and no_collision

# Resolve the player's attempted movement after direction has been set.
# For diagonal movement, try the full move first, then X-only, then Y-only.
def update_player_position(move_attempt_x: bool,
                           move_attempt_y: bool, 
                           player: Character,
                           delta_secs: float,
                           map_width: int,
                           map_height: int,
                           map_collision_rects: list[pygame.Rect]
                           ) -> None:
    
    # Skip movement calculations when neither axis has input.
    if not move_attempt_x and not move_attempt_y:
        return
    
    # Calculate the position the current direction and frame time would produce.
    proposed_x, proposed_y = player.get_proposed_new_position(delta_secs)

    # Try diagonal movement first. If blocked, slide along an available axis.
    if move_attempt_x and move_attempt_y:
        
        if is_proposed_player_move_valid(proposed_x,
                                         proposed_y,
                                         player,
                                         map_collision_rects,
                                         map_width,
                                         map_height):
            player.world_x = proposed_x
            player.world_y = proposed_y

        elif is_proposed_player_move_valid(proposed_x,
                                           player.world_y,
                                           player,
                                           map_collision_rects,
                                           map_width,
                                           map_height):
            player.world_x = proposed_x

        elif is_proposed_player_move_valid(player.world_x,
                                           proposed_y,
                                           player,
                                           map_collision_rects,
                                           map_width,
                                           map_height):
            player.world_y = proposed_y
        
    elif move_attempt_x:

        if is_proposed_player_move_valid(proposed_x,
                                         proposed_y,
                                         player,
                                         map_collision_rects,
                                         map_width,
                                         map_height):
            player.world_x = proposed_x

    elif move_attempt_y:

        if is_proposed_player_move_valid(proposed_x,
                                         proposed_y,
                                         player,
                                         map_collision_rects,
                                         map_width,
                                         map_height):
            player.world_y = proposed_y

def main() -> None:
    # Set up Pygame and create the game window.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Xiao map test")
    clock = pygame.time.Clock()

    # Load the Tiled map and its referenced tile images.
    tiled_map = load_pygame(MAP_PATH)

    # Convert the map dimensions from tiles into world pixels.
    map_height = tiled_map.height * tiled_map.tileheight
    map_width = tiled_map.width * tiled_map.tilewidth

    # Create the player-controlled Character using the Elf Mage's
    # sprite-specific alignment, collision, and visible-bound settings.
    player = Character(name="Elf Mage",
                    sprite_path=ELF_MAGE_FILE_PATH,
                    spawn_offset_x=ELF_MAGE_SPAWN_OFFSET_X,
                    spawn_offset_y=ELF_MAGE_SPAWN_OFFSET_Y,
                    collision_offset_x=ELF_MAGE_COLLISION_RECT_X,
                    collision_offset_y=ELF_MAGE_COLLISION_RECT_Y,
                    collision_box_height=ELF_MAGE_COLLISION_RECT_HEIGHT,
                    collision_box_width=ELF_MAGE_COLLISION_RECT_WIDTH,
                    default_speed=ELF_MAGE_PLAYER_SPEED,
                    visible_top_offset=ELF_MAGE_VISIBLE_TOP_OFFSET,
                    visible_bottom_offset=ELF_MAGE_VISIBLE_BOTTOM_OFFSET,
                    visible_left_offset=ELF_MAGE_VISIBLE_LEFT_OFFSET,
                    visible_right_offset=ELF_MAGE_VISIBLE_RIGHT_OFFSET
                    )
    
    # get player start location
    spawn_x, spawn_y = get_player_start(tiled_map)

    # can't use the Character on the map / in the world until we spawn()
    player.spawn(spawn_x, spawn_y)

    # get all the collision rects for our map
    map_collision_rects: list[pygame.Rect] = get_collision_rects(tiled_map)

    # Track whether this frame contains horizontal or vertical movement input.
    move_attempt_x: bool = False
    move_attempt_y: bool = False

    running = True

    while running:

        # clear movement from last frame. +1, 0, or -1. 
        player.direction_x = 0
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

        # Validate and apply the attempted movement against map bounds and obstacles.
        update_player_position(move_attempt_x,
                               move_attempt_y,
                               player,
                               delta_secs,
                               map_width,
                               map_height,
                               map_collision_rects)

        # Draw each visible tile layer from bottom to top.
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for tile_x, tile_y, tile_image in layer.tiles():
                    screen_x = tile_x * tiled_map.tilewidth
                    screen_y = tile_y * tiled_map.tileheight

                    screen.blit(tile_image, (screen_x, screen_y))
        
        # Draw the player sprite at its current world position.
        screen.blit(player.sprite,(player.world_x, player.world_y))

        # Make the completed frame visible
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()