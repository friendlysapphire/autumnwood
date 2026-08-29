from dataclasses import dataclass
from pathlib import Path

import pygame

from animation_state import AnimationState

PROJECT_ROOT = Path(__file__).parent
SPRITE_BASE_PATH = PROJECT_ROOT / "resources" / "spritepacks"

@dataclass(frozen=True)
class CharacterScaffold:

    # Character movement speed in pixels per second.
    default_speed: float

    # Pygame draws from the image's top-left, we want to be centered aroound the feet. w/o this adjustment
    # char would appear in world down and to right of where the spawn point visually appears on the map.
    spawn_offset_x: int
    spawn_offset_y: int

    # collision based on small rect around the feet, not whole sprite. defines a rect inside the sprite image
    # x and y are the top-left coord
    collision_offset_x: int
    collision_offset_y: int

    # Width and height of the character's collision box, measured within the sprite image.
    # The collision box is intentionally smaller than the full sprite so only the character's feet block movement.
    collision_rect_width: int
    collision_rect_height: int

    # lines in from edges of sprite image the charater (walking sprite) begins as solid. useful for drawing
    # up to edge of window correctly.
    visible_top_offset: int
    visible_bottom_offset: int
    visible_left_offset: int
    visible_right_offset: int

    # Define the ordered sprite-sheet frames available for each Character animation state.
    sprite_animation_rects: dict[AnimationState, tuple[pygame.Rect, ...]]

    sprite_file_path: Path


# -----

# Define the ordered sprite-sheet frames available for each Elf Mage animation state.
ELF_MAGE_SPRITE_ANIMS = {
    AnimationState.IDLE : (pygame.Rect(0, 0, 64, 64),
                           pygame.Rect(64, 0, 64, 64)),
    AnimationState.WALKING : (pygame.Rect(0, 64, 64, 64),
                              pygame.Rect(64, 64, 64, 64),
                              pygame.Rect(128, 64, 64, 64))
                           
}

ELF_MAGE_FILE_PATH = (
    SPRITE_BASE_PATH
    / "PixelWorldSprites"
    / "UnitsSprites"
    / "Units"
    / "ElfMage_64.png"
)

ELF_MAGE = CharacterScaffold(
    default_speed=120.0,
    spawn_offset_x=32,
    spawn_offset_y=52,
    collision_offset_x=23,
    collision_offset_y=44,
    collision_rect_width=18,
    collision_rect_height=6,
    visible_top_offset=12,
    visible_bottom_offset=15,
    visible_left_offset=19,
    visible_right_offset=16,
    sprite_animation_rects=ELF_MAGE_SPRITE_ANIMS,
    sprite_file_path=ELF_MAGE_FILE_PATH
    )

# ------






