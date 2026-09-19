from pathlib import Path

import pygame

from characters.character import Character
from characters.npcs import NPC

class ShopPanel:

    def __init__(self,
                 *,
                 screen: pygame.Surface,
                 resources_base_path: Path,
                 window_height: int,
                 window_width: int,
                 alpha:int = 180,
                 font: pygame.font.Font | None = None
                 ) -> None:
        

        self.resources_base_path = resources_base_path

        # todo load base images and compose base panel
        # set panel width and height based on loaded images
        self.panel_width = 10
        self.panel_height = 10

        self.window_height = window_height
        self.window_width = window_width
        self.panel_alpha = alpha
        self.screen = screen

        self.shop_active = False

        self.current_page_index:int = 0

        self.npc_shopkeeper: NPC | None = None
        self.player: Character | None = None

        if font is None:
            self.font = pygame.font.Font(None, 22)
        else:
            self.font = font

        self.shop_panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.shop_panel_surface.fill((0, 0, 0, self.panel_alpha))

    def open(self, npc: NPC, player: Character) -> None:

        if self.shop_active is True:
            raise RuntimeError("Shop is already active, can't open another one.")
        
        else:
            self.shop_active = True
            self.current_page_index:int = 0
            self.npc_shopkeeper = npc
            self.player = player

            self.draw()


    def close(self) -> None:
        self.shop_active = False
        self.current_page_index:int = 0
        self.npc_shopkeeper = None
        self.player = None
        

    def draw(self) -> None:
        print("drawing shop")