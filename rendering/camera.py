from world.game_map import GameMap

# Return the world coordinates that should appear at the window's top-left corner.
# Rendering code converts world coordinates to screen coordinates by subtracting
# this camera position; this function does not draw or translate any map objects.
def get_clamped_camera_position(*,
                                character_world_x: float,
                                character_world_y: float,
                                current_map: GameMap,
                                window_width: int,
                                window_height: int
                                ) -> tuple[float, float]:

    
    # Start with the camera position that would place the character's sprite origin
    # at the center of the window. This may be adjusted when the camera reaches a map edge.
    unclamped_camera_x = character_world_x - (window_width / 2)
    unclamped_camera_y = character_world_y - (window_height / 2)

    # Find the camera position where the window's right or bottom edge exactly reaches
    # the map edge. A map smaller than the window has no farther camera position, so use zero.
    max_camera_x = max(0, current_map.width - window_width)
    max_camera_y = max(0, current_map.height - window_height)

    # Keep the camera's top-left world position within the valid map range.
    # Near a map edge, the camera stops moving instead of showing space beyond the map.
    camera_x_with_min = max(0, unclamped_camera_x)
    camera_x = min(camera_x_with_min, max_camera_x)

    camera_y_with_min = max(0, unclamped_camera_y)
    camera_y = min(camera_y_with_min, max_camera_y)

    return camera_x, camera_y
