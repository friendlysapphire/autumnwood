from pathlib import Path

import pygame

from camera import get_clamped_camera_position
from character import AnimationState, Character
from debug_rendering import draw_debug_overlays
from game_map import GameMap
from map_render import draw_map
from messages import GameMessage, GameMessageDismissPolicy
from modifiers import SpeedModifier
from movement import update_character_position
from region_effects import  MapTransitionRegionEffect, SpeedRegionEffect, get_active_region_effects
from world_object import AppleTree


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
MESSAGES_PANEL_HEIGHT = 96
MESSAGES_PANEL_WIDTH = WINDOW_WIDTH - 40
MESSAGES_PANEL_ALPHA = 100

FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAPS_PATH = PROJECT_ROOT / "resources"
SPRITE_BASE_PATH = PROJECT_ROOT / "resources" / "spritepacks"
BASE_MAP_PATH = MAPS_PATH / "testmap2.tmx"

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
    SPRITE_BASE_PATH
    / "PixelWorldSprites"
    / "UnitsSprites"
    / "Units"
    / "ElfMage_64.png"
)

BEGIN_GAME_SPAWN_NAME = "player_start"

def main() -> None:
    # Set up Pygame and create the game window.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Autumnwood map test")
    clock = pygame.time.Clock()

    # font for messages
    messages_font = pygame.font.Font(None, 22)
    current_message: GameMessage | None = None

    # Load the initial map and unpack the runtime state used by the game loop.
    current_map = GameMap(BASE_MAP_PATH)

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
    spawn_x, spawn_y = current_map.get_spawn_coords(BEGIN_GAME_SPAWN_NAME)

    # can't use the Character on the map / in the world until we spawn()
    player.spawn(spawn_x, spawn_y)

    # Track whether this frame contains horizontal or vertical movement input.
    move_attempt_x: bool = False
    move_attempt_y: bool = False

    # debug map features toggle
    show_map_debug_features = False

    # dialog / message Surface
    messages_panel = pygame.Surface((MESSAGES_PANEL_WIDTH, MESSAGES_PANEL_HEIGHT), pygame.SRCALPHA)
    messages_panel.fill((0, 0, 0, MESSAGES_PANEL_ALPHA))

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
                    match event.key:

                        case pygame.K_BACKQUOTE:
                            show_map_debug_features = not show_map_debug_features

                        # E examines/interacts with world objects currently overlapping the player.
                        case pygame.K_e:  
                            intersecting_world_objects = current_map.get_world_objs_intersecting_character(character=player)

                            # process each world object intersecting w/ our player
                            for wobj in intersecting_world_objects:

                                if isinstance(wobj, AppleTree):
                                    current_message = GameMessage("You interacted with an Apple Tree!",
                                                                  GameMessageDismissPolicy.ON_MOVE_ATTEMPT)

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


        # Determine any effects caused by the regions curently occupied
        intersecting_regions = current_map.get_regions_intersecting_character(character=player)
        region_effects = get_active_region_effects(intersecting_regions=intersecting_regions)

        # Marshal pre-move effects that modify the upcoming movement.

        # the only pre-move effects are speed modifiers for now. pre_move_effects will eventually be 
        # non-speed modifiers that need pre-move processing.

        #pre_move_effects = []
        speed_modifiers: list[SpeedModifier] = []
        for effect in region_effects.pre_move_effects:

            if isinstance(effect, SpeedRegionEffect):
                speed_modifiers.append(effect)


        # TODO: process pre-move effects except for SpeedModifiers (which affect player positioning, below)

        # Validate and apply the attempted movement against map bounds and obstacles.
        update_character_position(
            move_attempt_x=move_attempt_x,
            move_attempt_y=move_attempt_y,
            player=player,
            delta_secs=delta_secs,
            current_map=current_map,
            speed_modifiers=speed_modifiers
        )

        # Determine any effects caused by the regions curently occupied
        intersecting_regions = current_map.get_regions_intersecting_character(character=player)
        region_effects = get_active_region_effects(intersecting_regions=intersecting_regions)
        
        # Process effects triggered by the player's position after movement resolves.
        for effect in region_effects.post_move_effects:

            if isinstance(effect, MapTransitionRegionEffect):
                # Replace the active map, regions, and dimensions with the transition destination.
                dest_path = MAPS_PATH / f"{effect.destination_map}.tmx"
                current_map = GameMap(dest_path)

                # Find the destination spawn in the new map and place the existing player there.
                spawn_x, spawn_y = current_map.get_spawn_coords(effect.destination_spawn)

                # can't use the Character on the map / in the world until we spawn()
                player.spawn(spawn_x, spawn_y)

        # perform actions based on player trying to move or not moving at all
            # Choose the animation state from this frame's movement input.
            # Clear ON_MOVE_ATETMPT current_messages (if there is one)
        if move_attempt_x or move_attempt_y:
            player.set_animation_state(AnimationState.WALKING)

            if current_message and current_message.dismiss_policy == GameMessageDismissPolicy.ON_MOVE_ATTEMPT:
                current_message = None
        else:

            player.set_animation_state(AnimationState.IDLE)

        camera_x, camera_y = get_clamped_camera_position(character_world_x=player.world_x,
                                                         character_world_y=player.world_y,
                                                         current_map=current_map,
                                                         window_width=WINDOW_WIDTH,
                                                         window_height=WINDOW_HEIGHT)


        draw_map(screen, current_map, camera_x, camera_y)

        # Advance the current animation based on elapsed frame time.
        player.update_sprite_animation(delta_secs)

        # Convert the player's world position to screen coordinates and draw the sprite.
        player_screen_x = round(player.world_x - camera_x)
        player_screen_y = round(player.world_y - camera_y)
        screen.blit(player.sprite, (player_screen_x, player_screen_y))

        # process and display game messages (anything in messages panel)
        if current_message:

            timer_expired = False

            # if current_message is TIMED, count down and maybe expire
            if current_message.dismiss_policy == GameMessageDismissPolicy.TIMED:

                current_message.remaining_secs -= delta_secs
                if current_message.remaining_secs <= 0:
                    current_message = None
                    timer_expired = True

            if not timer_expired:
                # clear any previous messages in the panel
                messages_panel.fill((0, 0, 0, MESSAGES_PANEL_ALPHA))

                message_surface = messages_font.render(current_message.text, True, "grey87")
                messages_panel.blit(message_surface, (20,20)) 
                screen.blit(messages_panel, (20, WINDOW_HEIGHT - MESSAGES_PANEL_HEIGHT))

        # Draw optional region and collision debug overlays on top of the completed scene.
        if show_map_debug_features:
           draw_debug_overlays(screen=screen,
                               current_map=current_map,
                               player=player,
                               camera_x=camera_x,
                               camera_y=camera_y)

        # Make the completed frame visible
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
