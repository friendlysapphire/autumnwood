from game_map import GameMap

# Recalculate the camera after movement so it follows the player's current world position.
def get_clamped_camera_position(*,
                                character_world_x: float,
                                character_world_y: float,
                                current_map: GameMap,
                                window_width: int,
                                window_height: int
                                ) -> tuple[float, float]:

    
    # Calculate the camera position that would place the player's sprite origin
    # at the center of the screen.
    unclamped_camera_x = character_world_x - (window_width / 2)
    unclamped_camera_y = character_world_y - (window_height / 2)

    # Find the farthest valid camera position on each axis.
    # Keeping these values nonnegative also handles maps smaller than the window.
    max_camera_x = max(0, current_map.width - window_width)
    max_camera_y = max(0, current_map.height - window_height)

    # Clamp each camera coordinate between zero and its maximum valid position.
    camera_x_with_min = max(0, unclamped_camera_x)
    camera_x = min(camera_x_with_min, max_camera_x)

    camera_y_with_min = max(0, unclamped_camera_y)
    camera_y = min(camera_y_with_min, max_camera_y)

    return camera_x, camera_y