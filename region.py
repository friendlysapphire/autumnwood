from dataclasses import dataclass
from enum import StrEnum
import pygame


class RegionType(StrEnum):
    SOLID = "solid"

@dataclass
class Region:

    def __init__(self,
                 *,
                 rect: pygame.rect,
                 type: RegionType
                 ) -> None:

        self.rect = rect
        self.type = type
