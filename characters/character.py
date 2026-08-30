from collections.abc import Sequence
from typing import Literal

import pygame

from characters.animation_state import AnimationState
from characters.character_scaffolds import CharacterScaffold
from modifiers import SpeedModifier

type DirectionValue = Literal[-1, 0, 1]


# Character owns character-specific state, animation, and movement math.
# Map collision policy belongs to the movement/world systems instead.
class Character:
    def __init__(
        self,
        *,
        name: str,
        display_name: str,
        scaffold: CharacterScaffold
    ):

        self.name = name
        self.is_alive = True
        self.scaffold = scaffold
        self.display_name = display_name

        self.speed = self.scaffold.default_speed

        # These values are initialized by spawn().
        # Until then, the character exists but has not been placed in the world.
        self.world_x: float | None = None
        self.world_y: float | None = None
        self.direction_x: DirectionValue = 0
        self.direction_y: DirectionValue = 0

        # set up our initial sprite 
        sprite_sheet = pygame.image.load(self.scaffold.sprite_file_path)

        # convert_alpha() requires Pygame's display mode to already exist.
        # Note: Constructing a Character (ie this code) therefore depends on display initialization.
        self._sprite_sheet = sprite_sheet.convert_alpha()

        sprite_idle_rects = self.scaffold.sprite_animation_rects.get(AnimationState.IDLE)

        if not sprite_idle_rects:
            raise ValueError("sprite_animation_rects must include at least one IDLE frame.")

        # Use the first idle frame as the character's initial visible sprite.
        self.sprite = self._sprite_sheet.subsurface(sprite_idle_rects[0])

        # Track the active animation, its current frame, and elapsed time between frame changes.
        self._current_animation_state = AnimationState.IDLE
        self._current_animation_state_num_frames = len(self.scaffold.sprite_animation_rects[AnimationState.IDLE])

        self._current_frame_index = 0
        self._animation_elapsed_time = 0.0
        self._seconds_per_sprite_anim_frame = 0.25
             
        # Track whether spawn() has placed the character on the map.
        # Position-dependent methods should not run before this becomes True.
        self.spawned = False

    # Place the character on the map and establish the world position used from this point forward.
    def spawn(
        self,
        x: float,
        y: float,
        direction_x: DirectionValue = 0,
        direction_y: DirectionValue = 0,
    ) -> None:

        self.world_x = x - self.scaffold.spawn_offset_x
        self.world_y = y - self.scaffold.spawn_offset_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.spawned = True

    # Return the character's collision rectangle at its current world position,
    # or at a supplied position when testing a proposed move.
    def get_collision_rect(
        self, x: float | None = None, y: float | None = None
    ) -> pygame.Rect:

        if not self.spawned:
            raise RuntimeError(
                f"Character {self.name} must be spawned to generate a collision rect."
            )

        # Use the character's current position when no coordinates are supplied.
        # Explicit coordinates let us test a proposed position before actually moving it.
        if x is None and y is None:
            use_x = self.world_x
            use_y = self.world_y
        elif x is not None and y is not None:
            use_x = x
            use_y = y
        else:
            raise ValueError(
                "In get_collision_rect both x and y must be none or both must be a value."
            )

        return pygame.Rect(
            use_x + self.scaffold.collision_offset_x,
            use_y + self.scaffold.collision_offset_y,
            self.scaffold.collision_rect_width,
            self.scaffold.collision_rect_height
            )

    # Calculate where the current direction and speed would move the character
    # without changing its actual world position.
    def get_proposed_new_position(self, delta_secs: float, 
                                  speed_modifiers: Sequence[SpeedModifier] = ()
                                  ) -> tuple[float, float]:


        # Calculate the combined percentage change from all active speed modifiers.
        # Applying both direction components at full speed makes diagonal movement faster.
        aggregate_pct_change = sum(m.percent_change for m in speed_modifiers)

        # Apply the temporary modifiers without changing the character's stored speed.
        effective_speed = self.speed * (1 + aggregate_pct_change)

        new_x = self.world_x + (self.direction_x * effective_speed * delta_secs)
        new_y = self.world_y + (self.direction_y * effective_speed * delta_secs)

        return (new_x, new_y)

    # Check whether the character's visible walking-sprite bounds fit inside
    # the supplied rectangular area, ignoring transparent padding around the frame.
    # currently used for testing against map edges.
    def is_within_bounds(
        self, proposed_x: float, proposed_y: float, x_size: int, y_size: int
    ) -> bool:

        in_bounds = (
            proposed_x + self.scaffold.visible_left_offset >= 1
            and proposed_x + self.sprite.get_width() - self.scaffold.visible_right_offset <= x_size
            and proposed_y + self.scaffold.visible_top_offset >= 1
            and proposed_y + self.sprite.get_height() - self.scaffold.visible_bottom_offset <= y_size
        )
        return in_bounds

    # Change to the requested animation when this character has frames for it.
    # Otherwise, fall back to IDLE. Reset only when the effective state actually changes.
    def set_animation_state(self, state: AnimationState) -> None:

        # Resolve the requested state to one this character can actually display.
        state_rects = self.scaffold.sprite_animation_rects.get(state)
        if state_rects:
            new_state = state
        else:
            new_state = AnimationState.IDLE

        if new_state == self._current_animation_state:
            return

        # Start the new animation from its first frame and reset its timer.
        self._current_animation_state = new_state
        self._current_animation_state_num_frames = len(self.scaffold.sprite_animation_rects[self._current_animation_state])
        self._animation_elapsed_time = 0.0
        self._current_frame_index = 0

        anim_rects = self.scaffold.sprite_animation_rects[self._current_animation_state]
        self.sprite = self._sprite_sheet.subsurface(anim_rects[self._current_frame_index])
        
    # Accumulate elapsed time and advance the active animation when one frame interval has passed.
    def update_sprite_animation(self, delta_secs: float) -> None:

        self._animation_elapsed_time += delta_secs

        # Keep the current frame until enough time has passed to advance.
        if self._animation_elapsed_time >= self._seconds_per_sprite_anim_frame:

            # Advance to the next frame, wrapping back to frame zero at the end.
            self._current_frame_index = (self._current_frame_index + 1) % self._current_animation_state_num_frames

            self._animation_elapsed_time = 0.0

            # Replace the visible sprite with the newly selected animation frame.
            anim_rects = self.scaffold.sprite_animation_rects[self._current_animation_state]
            self.sprite = self._sprite_sheet.subsurface(anim_rects[self._current_frame_index])


