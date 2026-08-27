from collections.abc import Sequence

from character import Character
from game_map import GameMap
from modifiers import SpeedModifier

# This module applies world movement policy. Character calculates a proposed position;
# this module decides whether the current map allows it and resolves collision sliding.

# A proposed position is valid only if the character stays within the map
# and does not overlap a region that blocks movement.
def is_proposed_player_move_valid(
        *,
        proposed_x: float,
        proposed_y: float,
        char: Character,
        current_map: GameMap
        ) -> bool:

    in_bounds = char.is_within_bounds(
        proposed_x,
        proposed_y,
        x_size=current_map.width,
        y_size=current_map.height,
    )

    player_collision_rect = char.get_collision_rect(proposed_x, proposed_y)

    # Check the proposed player collision box against regions that are not walkable by default.
    for region in current_map.regions:

        if not region.is_walkable_by_default():
            if player_collision_rect.colliderect(region.rect):
                return False

    return in_bounds

# Resolve the player's attempted movement after direction has been set.
# For diagonal movement, try the full move first, then X-only, then Y-only.
def update_character_position(
    *,
    move_attempt_x: bool,
    move_attempt_y: bool,
    player: Character,
    delta_secs: float,
    current_map: GameMap,
    speed_modifiers: Sequence[SpeedModifier]
) -> None:

    # Skip movement calculations when neither axis has input.
    if not move_attempt_x and not move_attempt_y:
        return

    # Calculate the position the current direction and frame time would produce.
    proposed_x, proposed_y = player.get_proposed_new_position(delta_secs, speed_modifiers)

    # Try diagonal movement first. If blocked, slide along an available axis.
    # X receives priority when both axis-only moves are valid.
    if move_attempt_x and move_attempt_y:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            current_map=current_map
        ):
            player.world_x = proposed_x
            player.world_y = proposed_y

        elif is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=player.world_y,
            char=player,
            current_map=current_map
        ):
            player.world_x = proposed_x

        elif is_proposed_player_move_valid(
            proposed_x=player.world_x,
            proposed_y=proposed_y,
            char=player,
            current_map=current_map
        ):
            player.world_y = proposed_y

    elif move_attempt_x:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            current_map=current_map
        ):
            player.world_x = proposed_x

    elif move_attempt_y:
        if is_proposed_player_move_valid(
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            char=player,
            current_map=current_map
        ):
            player.world_y = proposed_y
