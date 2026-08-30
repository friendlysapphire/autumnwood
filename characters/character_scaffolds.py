from dataclasses import dataclass
from pathlib import Path

import pygame

from characters.animation_state import AnimationState

PROJECT_ROOT = Path(__file__).parent.parent
SPRITE_BASE_PATH = PROJECT_ROOT / "resources" / "spritepacks"

@dataclass(frozen=True, kw_only=True)
class CharacterScaffold:

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
    # TODO 
    # this is a frozen dataclass but the dict and these rects are mutable. when python 3.15 is avail, make this a frozendict
    # then just don't worry about the pygame.Rect mutablility.... we're never going to want to hash this. i just 
    # want to learn about these language features 
    sprite_animation_rects: dict[AnimationState, tuple[pygame.Rect, ...]]

    sprite_file_path: Path

    # Character movement speed in pixels per second.
    default_speed: float = 120.0


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

# The vendor sheet has eight 128x128 idle frames in one horizontal row.
TRAVELING_VENDOR_SPRITE_ANIMS = {
    AnimationState.IDLE: (
        pygame.Rect(0, 0, 128, 128),
        pygame.Rect(128, 0, 128, 128),
        pygame.Rect(256, 0, 128, 128),
        pygame.Rect(384, 0, 128, 128),
        pygame.Rect(512, 0, 128, 128),
        pygame.Rect(640, 0, 128, 128),
        pygame.Rect(768, 0, 128, 128),
        pygame.Rect(896, 0, 128, 128),
    ),
}

TRAVELING_VENDOR_FILE_PATH = (
    SPRITE_BASE_PATH
    / "epicrpg"
    / "grassland2.1"
    / "Characters"
    / "vendor-idle.png"
)

TRAVELING_VENDOR = CharacterScaffold(
    # This first NPC is designed to be stationary in the art pack,
    # so it has no WALKING frames... but let's allow it to move slowly
    default_speed=75.0,

    # Tiled spawn coordinates represent the vendor's approximate feet-center.
    spawn_offset_x=64,
    spawn_offset_y=89,

    # Initial small body/feet collision rectangle. Verify visually once rendered.
    collision_offset_x=57,
    collision_offset_y=81,
    collision_rect_width=14,
    collision_rect_height=6,

    # Measured transparent margins around the vendor's 128x128 idle frames.
    visible_top_offset=33,
    visible_bottom_offset=39,
    visible_left_offset=44,
    visible_right_offset=46,

    sprite_animation_rects=TRAVELING_VENDOR_SPRITE_ANIMS,
    sprite_file_path=TRAVELING_VENDOR_FILE_PATH,
)
