from pathlib import Path
from typing import Literal

import pygame

type DirectionValue = Literal[-1, 0, 1]


class Character:
    def __init__(
        self,
        *,
        name: str,
        sprite_path: str | Path,
        spawn_offset_x: int,
        spawn_offset_y: int,
        collision_offset_x: int,
        collision_offset_y: int,
        collision_box_height: int,
        collision_box_width: int,
        default_speed: float,
        visible_top_offset: int = 0,
        visible_bottom_offset: int = 0,
        visible_left_offset: int = 0,
        visible_right_offset: int = 0,
    ):

        self.name = name

        if isinstance(sprite_path, Path):
            self._sprite_path = sprite_path
        else:
            self._sprite_path = Path(sprite_path)

        # We apply these values once on spawn so the character appears centered at the spawn location.
        # Otherwise, the sprite's top-left corner would start at the spawn location,
        # making the character appear down and to the right.
        self._spawn_offset_x = spawn_offset_x
        self._spawn_offset_y = spawn_offset_y

        # These x and y offsets define the collision box's top-left corner
        # relative to the sprite, typically around the character's feet.
        # (we are offsetting into the sprite image here to find the top left of the feet (or where we want
        # the collision rect to be based))
        self._collision_offset_x = collision_offset_x
        self._collision_offset_y = collision_offset_y

        # how much height and width the collision box should be from the top left defined by collision_offset_x and y
        self._collision_box_height = collision_box_height
        self._collision_box_width = collision_box_width

        # speed in pixels per second
        self._default_speed = default_speed
        self.speed = default_speed

        # These offsets describe the transparent padding around the walking sprite.
        # They let us test the character's visible, solid body against the map edges instead
        # of using the full 64x64 frame, which includes empty space.
        # Other animations may extend beyond these walking-frame bounds.
        self.visible_top_offset = visible_top_offset
        self.visible_bottom_offset = visible_bottom_offset
        self.visible_left_offset = visible_left_offset
        self.visible_right_offset = visible_right_offset

        # These values are initialized by spawn().
        # Until then, the character exists but has not been placed in the world.
        self.world_x: float | None = None
        self.world_y: float | None = None
        self.direction_x: DirectionValue = 0
        self.direction_y: DirectionValue = 0

        # set up our sprite
        player_sprite_sheet = pygame.image.load(self._sprite_path)

        # convert_alpha() requires Pygame's display mode to already exist.
        # Note: Constructing a Character (ie this code) therefore depends on display initialization.
        player_sprite_sheet = player_sprite_sheet.convert_alpha()

        # TODO: This hard-coded rectangle selects the Elf Mage's first frame.
        # Move character-specific sprite-sheet details into an animation or sprite configuration later.
        sprite_rect = pygame.Rect(0, 0, 64, 64)

        self.sprite = player_sprite_sheet.subsurface(sprite_rect)

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

        self.world_x = x - self._spawn_offset_x
        self.world_y = y - self._spawn_offset_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.spawned = True

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

        # Translate the sprite's top-left world position to the collision box's position.
        return pygame.Rect(
            use_x + self._collision_offset_x,
            use_y + self._collision_offset_y,
            self._collision_box_width,
            self._collision_box_height,
        )

    # Calculate where the current direction and speed would move the character
    # without changing its actual world position.
    def get_proposed_new_position(self, delta_secs: float) -> tuple[float, float]:

        new_x = self.world_x + (self.direction_x * self.speed * delta_secs)
        new_y = self.world_y + (self.direction_y * self.speed * delta_secs)

        return (new_x, new_y)

    # Check whether the character's visible walking-sprite bounds fit inside
    # the supplied rectangular area, ignoring transparent padding around the frame.
    # currently used for testing against map edges.
    def is_within_bounds(
        self, proposed_x: float, proposed_y: float, x_size: int, y_size: int
    ) -> bool:

        in_bounds = (
            proposed_x + self.visible_left_offset >= 1
            and proposed_x + self.sprite.get_width() - self.visible_right_offset
            <= x_size
            and proposed_y + self.visible_top_offset >= 1
            and proposed_y + self.sprite.get_height() - self.visible_bottom_offset
            <= y_size
        )
        return in_bounds
