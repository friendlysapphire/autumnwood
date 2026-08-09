from character import Character, AnimationState
from pathlib import Path
from pytmx.util_pygame import load_pygame
from region import Region, RegionType

import pygame
import pytmx



WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640

FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAP_PATH = PROJECT_ROOT / "resources" / "testmap2.tmx"


# Elf Mage player construction details
# player speed is in pixels per second
ELF_MAGE_PLAYER_SPEED = 120.0

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

# Define the ordered sprite-sheet frames available for each Elf Mage animation state.
ELF_MAGE_SPRITE_ANIMS = {
    AnimationState.IDLE : [pygame.Rect(0, 0, 64, 64),
                           pygame.Rect(64, 0, 64, 64)],
    AnimationState.WALKING : [pygame.Rect(0, 64, 64, 64),
                              pygame.Rect(64, 64, 64, 64),
                              pygame.Rect(128, 64, 64, 64)]
                           
}

ELF_MAGE_FILE_PATH = (
    PROJECT_ROOT
    / "resources"
    / "PixelWorldSprites"
    / "UnitsSprites"
    / "Units"
    / "ElfMage_64.png"
)

# Recalculate the camera after movement so it follows the player's current world position.
def get_clamped_camera_position(*,
                                character_world_x: float,
                                character_world_y: float, 
                                map_width: int,
                                map_height: int,
                                window_width: int,
                                window_height: int
                                ) -> tuple[float, float]:

    
    # Calculate the camera position that would place the player's sprite origin
    # at the center of the screen.
    unclamped_camera_x = character_world_x - (window_width / 2)
    unclamped_camera_y = character_world_y - (window_height / 2)

    # Find the farthest valid camera position on each axis.
    # Keeping these values nonnegative also handles maps smaller than the window.
    max_camera_x = max(0, map_width - window_width)
    max_camera_y = max(0, map_height - window_height)

    # Clamp each camera coordinate between zero and its maximum valid position.
    camera_x_with_min = max(0, unclamped_camera_x)
    camera_x = min(camera_x_with_min, max_camera_x)

    camera_y_with_min = max(0, unclamped_camera_y)
    camera_y = min(camera_y_with_min, max_camera_y)

    return camera_x, camera_y

# Load gameplay regions from Tiled.
# Collision-layer objects are always SOLID; Regions-layer objects define their type explicitly.
def get_map_regions(tiled_map: pytmx.TiledMap) -> list[Region]:

    region_list: list[Region] = []

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Collisions":
                for obj in layer:
                    crect: pygame.Rect = pygame.Rect(obj.x, 
                                                     obj.y, 
                                                     obj.width, 
                                                     obj.height)
                    
                    region_list.append(Region(rect=crect, type=RegionType.SOLID))

            if layer.name == "Regions":
                for obj in layer:
                    region_rect = pygame.Rect(obj.x,
                                              obj.y,
                                              obj.width,
                                              obj.height)

                    r_type = obj.properties.get("region_type")

                    if r_type:
                            region_list.append(Region(rect=region_rect, type=RegionType(r_type)))
                    else:
                        raise ValueError(f"All objects in Regions layer need region_type: {obj.x}: {obj.y} : {obj.properties}")

                        
    return region_list


# Find the named player spawn point in Tiled and return its world coordinates.
def get_player_start(tiled_map: pytmx.TiledMap) -> tuple[float, float]:

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Spawns":
                for obj in layer:
                    if obj.name == "player_start":
                        return (obj.x, obj.y)

    raise ValueError("Could not find initial player start location.")


# Check the proposed player collision box against regions that are not walkable by default.
def is_proposed_player_move_valid(
    *,
    proposed_x: float,
    proposed_y: float,
    char: Character,
    map_regions: list[Region],
    map_width: int,
    map_height: int,
) -> bool:

    in_bounds = char.is_within_bounds(
        proposed_x, proposed_y, x_size=map_width, y_size=map_height
    )

    player_collision_rect = char.get_collision_rect(proposed_x, proposed_y)
    no_collision = True

    # Check the proposed player collision box against regions that currently block movement.
    for region in map_regions:
        if not region.is_walkable_by_default():
            if player_collision_rect.colliderect(region.rect):
                no_collision = False
                break

    return in_bounds and no_collision


# Resolve the player's attempted movement after direction has been set.
# For diagonal movement, try the full move first, then X-only, then Y-only.
def update_player_position(
    *,
    move_attempt_x: bool,
    move_attempt_y: bool,
    player: Character,
    delta_secs: float,
    map_width: int,
    map_height: int,
    map_regions: list[Region],
) -> None:

    # Skip movement calculations when neither axis has input.
    if not move_attempt_x and not move_attempt_y:
        return

    # Calculate the position the current direction and frame time would produce.
    proposed_x, proposed_y = player.get_proposed_new_position(delta_secs)

    # Try diagonal movement first. If blocked, slide along an available axis.
    if move_attempt_x and move_attempt_y:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            map_regions=map_regions,
            map_width=map_width,
            map_height=map_height,
        ):
            player.world_x = proposed_x
            player.world_y = proposed_y

        elif is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=player.world_y,
            char=player,
            map_regions=map_regions,
            map_width=map_width,
            map_height=map_height,
        ):
            player.world_x = proposed_x

        elif is_proposed_player_move_valid(
            proposed_x=player.world_x,
            proposed_y=proposed_y,
            char=player,
            map_regions=map_regions,
            map_width=map_width,
            map_height=map_height,
        ):
            player.world_y = proposed_y

    elif move_attempt_x:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            map_regions=map_regions,
            map_width=map_width,
            map_height=map_height,
        ):
            player.world_x = proposed_x

    elif move_attempt_y:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            map_regions=map_regions,
            map_width=map_width,
            map_height=map_height,
        ):
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
    # animation, alignment, collision, and visible-bound settings.
    player = Character(
        name="Elf Mage",
        sprite_path=ELF_MAGE_FILE_PATH,
        sprite_animation_rects=ELF_MAGE_SPRITE_ANIMS,
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
        visible_right_offset=ELF_MAGE_VISIBLE_RIGHT_OFFSET,
    )

    # get player start location
    spawn_x, spawn_y = get_player_start(tiled_map)

    # can't use the Character on the map / in the world until we spawn()
    player.spawn(spawn_x, spawn_y)


    # Load the gameplay regions defined in the map.
    map_regions: list[Region] = get_map_regions(tiled_map)

    # Track whether this frame contains horizontal or vertical movement input.
    move_attempt_x: bool = False
    move_attempt_y: bool = False

    # debug map features toggle
    show_map_debug_features = False

    running = True

    while running:
        # clear movement from last frame. +1, 0, or -1.
        player.direction_x = 0
        player.direction_y = 0

        # clear flag showing attempted movement from last frame
        move_attempt_x = False
        move_attempt_y = False

        # get ms since last frame
        elapsed_ms = clock.tick(FRAMES_PER_SECOND)
        delta_secs = elapsed_ms / 1000

        # Read pending window and input events.
        for event in pygame.event.get():
            
            match event.type:
                case pygame.QUIT:
                    running = False

                case pygame.KEYDOWN:
                    if event.key == pygame.K_BACKQUOTE:
                        show_map_debug_features = not show_map_debug_features


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
        update_player_position(
            move_attempt_x=move_attempt_x,
            move_attempt_y=move_attempt_y,
            player=player,
            delta_secs=delta_secs,
            map_width=map_width,
            map_height=map_height,
            map_regions=map_regions,
        )

        camera_x, camera_y = get_clamped_camera_position(character_world_x=player.world_x,
                                                         character_world_y=player.world_y, 
                                                         map_width=map_width,
                                                         map_height=map_height,
                                                         window_width=WINDOW_WIDTH,
                                                         window_height=WINDOW_HEIGHT)

        camera_screen_offset_x = round(-camera_x)
        camera_screen_offset_y = round(-camera_y)

        # Choose the animation state from this frame's movement input.
        if move_attempt_x or move_attempt_y:
            player.set_animation_state(AnimationState.WALKING)
        else:
            player.set_animation_state(AnimationState.IDLE)

        # Draw each visible tile layer from bottom to top.
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for tile_x, tile_y, tile_image in layer.tiles():
                    tile_world_x = tile_x * tiled_map.tilewidth
                    tile_world_y = tile_y * tiled_map.tileheight
                    tile_screen_x = round(tile_world_x - camera_x)
                    tile_screen_y = round(tile_world_y - camera_y)

                    # Convert the tile's world position to its position inside the camera view.
                    screen.blit(tile_image, (tile_screen_x, tile_screen_y))

        # Advance the current animation based on elapsed frame time.
        player.update_sprite_animation(delta_secs)

        # Convert the player's world position to screen coordinates and draw the sprite.
        player_screen_x = round(player.world_x - camera_x)
        player_screen_y = round(player.world_y - camera_y)
        screen.blit(player.sprite, (player_screen_x, player_screen_y))

        # Draw optional region and collision debug overlays on top of the completed scene.
        if show_map_debug_features:
           
            # Shift each region rectangle into screen coordinates for debug drawing.
            for region in map_regions:
                region_rect = region.rect

                # Use distinct colors so different region types are easy to identify while debugging.
                match region.type:
                    case RegionType.SOLID:
                        col_str = "darkorange"
                    case RegionType.NAVIGABLE_DEEP_WATER:
                        col_str = "cornsilk"
                    case RegionType.NAVIGABLE_SHALLOW_WATER:
                        col_str = "coral2"
                    case _:
                        col_str = "chocolate4"

                camera_adjusted_rect = region_rect.move(camera_screen_offset_x, camera_screen_offset_y)
                pygame.draw.rect(screen, pygame.Color(col_str), camera_adjusted_rect, width=2)
            
            # Shift the player's collision rectangle into screen coordinates for debug drawing.
            base_player_crect = player.get_collision_rect()
            camera_adjusted_rect = base_player_crect.move(camera_screen_offset_x, camera_screen_offset_y)
            pygame.draw.rect(screen, pygame.Color('darkorchid1'), camera_adjusted_rect, width=2)

        # Make the completed frame visible
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
