from pathlib import Path

import pygame

from animation_state import AnimationState
from camera import get_clamped_camera_position
from character import Character
from character_scaffolds import ELF_MAGE
from debug_rendering import draw_debug_overlays
from game_map import GameMap
from map_render import draw_map
from notifications import GameNotification, GameNotificationDismissPolicy, NotificationPanel
from movement import update_character_position
from region_effects import  MapTransitionRegionEffect, SpeedRegionEffect, get_active_region_effects
from world_object import AppleTree


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
NOTIFICATION_PANEL_HEIGHT = 96
NOTIFICATION_PANEL_WIDTH = WINDOW_WIDTH - 40
NOTIFICATION_PANEL_ALPHA = 100

FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAPS_PATH = PROJECT_ROOT / "resources"
BASE_MAP_PATH = MAPS_PATH / "testmap2.tmx"

BEGIN_GAME_SPAWN_NAME = "player_start"

def main() -> None:
    # Set up Pygame and create the game window.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Autumnwood map test")
    clock = pygame.time.Clock()

    # The panel owns active-notification lifecycle state and its presentation.
    notification_panel = NotificationPanel(screen=screen,
                                           panel_width=NOTIFICATION_PANEL_WIDTH,
                                           panel_height=NOTIFICATION_PANEL_HEIGHT,
                                           window_height=WINDOW_HEIGHT,
                                           alpha=NOTIFICATION_PANEL_ALPHA)
    
    # Load the initial map, which owns its runtime regions, world objects, and dimensions.
    current_map = GameMap(BASE_MAP_PATH)

    # Create the player-controlled Character using the Elf Mage's
    # animation, alignment, collision, and visible-bound settings.
    player = Character(name="player", display_name="Player", scaffold=ELF_MAGE)

    # get player start location
    spawn_x, spawn_y = current_map.get_player_spawn_coords(BEGIN_GAME_SPAWN_NAME)

    # can't use the Character on the map / in the world until we spawn()
    player.spawn(spawn_x, spawn_y)

    # Spawn only NPCs authored to appear when this map loads. Delayed NPCs remain in
    # current_map.npcs so a future trigger can place them at their initial map location.
    for npc in current_map.npcs:
        if npc.spawn_on_map_load:
            npc.spawn_from_initial_map_placement()

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
                    match event.key:

                        case pygame.K_BACKQUOTE:
                            show_map_debug_features = not show_map_debug_features

                        # E examines/interacts with world objects currently overlapping the player.
                        case pygame.K_e:  
                            intersecting_world_objects = current_map.get_world_objs_intersecting_character(character=player)

                            # process each world object intersecting w/ our player
                            for wobj in intersecting_world_objects:

                                if isinstance(wobj, AppleTree):
                                    note = GameNotification("You interacted with an Apple Tree!",
                                                            GameNotificationDismissPolicy.ON_MOVE_ATTEMPT)

                                    notification_panel.set_notification(note)

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


        # Discover effects from the position occupied before movement. These effects can
        # modify the upcoming move, such as quicksand changing the effective speed.
        intersecting_regions = current_map.get_regions_intersecting_character(character=player)
        region_effects = get_active_region_effects(intersecting_regions=intersecting_regions)

        # Extract the speed modifiers currently needed by movement. Other pre-move effect
        # types can be processed here when a gameplay feature introduces them.

        #pre_move_effects = []
        speed_modifiers = [effect
                           for effect
                           in region_effects.pre_move_effects
                           if isinstance(effect, SpeedRegionEffect)]

        # TODO: process future pre-move effects other than SpeedModifiers, which affect positioning below.

        # Validate and apply the attempted movement against map bounds and obstacles.
        update_character_position(
            move_attempt_x=move_attempt_x,
            move_attempt_y=move_attempt_y,
            player=player,
            delta_secs=delta_secs,
            current_map=current_map,
            speed_modifiers=speed_modifiers
        )

        # Rediscover effects from the resolved position. Post-move effects, such as map
        # transitions, must use this position rather than the one from before movement.
        intersecting_regions = current_map.get_regions_intersecting_character(character=player)
        region_effects = get_active_region_effects(intersecting_regions=intersecting_regions)
        
        # Process effects triggered by the player's position after movement resolves.
        for effect in region_effects.post_move_effects:

            if isinstance(effect, MapTransitionRegionEffect):
                # Replace the active GameMap, then respawn the existing player at the
                # named destination spawn in that map.
                dest_path = MAPS_PATH / f"{effect.destination_map}.tmx"
                current_map = GameMap(dest_path)

                spawn_x, spawn_y = current_map.get_player_spawn_coords(effect.destination_spawn)

                player.spawn(spawn_x, spawn_y)

                # Apply each destination NPC's map-load policy after replacing the active map.
                for npc in current_map.npcs:
                    if npc.spawn_on_map_load:
                        npc.spawn_from_initial_map_placement()

        # Animation follows input intent, even when the map blocks the attempted move.
        # An attempted move also dismisses notifications that use that dismissal policy.
        if move_attempt_x or move_attempt_y:

            player.set_animation_state(AnimationState.WALKING)

            # Dismiss notifications whose policy is based on a movement attempt.
            notification_panel.notify_move_attempted()

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

        # Advance and draw only NPCs that currently exist in this map's runtime world.
        for npc in current_map.npcs:

            if npc.spawned:
                # Advance the current animation based on elapsed frame time.
                npc.update_sprite_animation(delta_secs)
        
            # Convert this NPC's world position to screen coordinates and draw its sprite.
                npc_screen_x = round(npc.world_x - camera_x)
                npc_screen_y = round(npc.world_y - camera_y)
                screen.blit(npc.sprite, (npc_screen_x, npc_screen_y))


        # Advance notification lifecycle and draw the panel above the completed world scene.
        notification_panel.update_and_draw(delta_secs=delta_secs)

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
