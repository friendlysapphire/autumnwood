from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import pygame

from items.item_id import ItemId

MAX_ITEM_DESCRIPTION_CHARS = 40

@dataclass(frozen=True)
class Item:

    id: ItemId 
    display_name: str
    icon_path: Path
    
    # sellers may have different markups, this is the base value
    default_gold_value: int

    # max ItemBundle size (max size per inventory slot)
    max_bundle_qty: int = 999

    description: str = ""

    # can't set this using post_init because it'll load (in item_catalog.py) before pygame is set up and fail
    @cached_property
    def icon_surface(self) -> pygame.Surface:
        return pygame.image.load(self.icon_path).convert_alpha()

    def __post_init__(self):
        if len(self.description) > MAX_ITEM_DESCRIPTION_CHARS:
            raise ValueError(f"Item {self} can not have description longer than {MAX_ITEM_DESCRIPTION_CHARS}")
