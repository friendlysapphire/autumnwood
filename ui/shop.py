from pathlib import Path

import pygame

from characters.character import Character
from characters.npcs import NPC

# TODO: lot of hard coded values in here that will need updates if we ever change the window size or
# make it user modifiable

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

        # build a base image w/ all the static components of the shop panel so draw() can 
        # focus on the dynamic bits
        self._init_shop_panel()


    def open(self, npc: NPC, player: Character) -> None:

        if self.shop_active is True:
            raise RuntimeError("Shop is already active, can't open another one.")
        
        else:
            self.shop_active = True
            self.current_page_index = 0
            self.npc_shopkeeper = npc
            self.player = player

            self.draw()


    def close(self) -> None:
        self.shop_active = False
        self.current_page_index = 0
        self.npc_shopkeeper = None
        self.player = None


    def draw(self) -> None:
        if self.shop_active:

            # Clear the previous 
            self.shop_base_surface.fill((0, 0, 0, self.panel_alpha))

            # lay down the basic, static structure
            self.shop_base_surface.blit(self.shop_base_img, (0,0))

            # add vendor's displayname
            display_name = self.font.render(self.npc_shopkeeper.display_name, True, "grey87")
            self.shop_base_surface.blit(display_name, (25,10))

            # TODO: choose buy/sell based on whether we've selected vendor or player inventory
            footer = "Buy"
            footer_fmt = self.font.render(footer, True, "grey87")
            self.shop_base_surface.blit(footer_fmt, (315, 400))
 
            self.screen.blit(self.shop_base_surface, (96,123))

    # INTERNAL ONLY HELPERS

    def _init_shop_panel(self) -> None:

        shop_frame_img_path = self.resources_base_path / "UI" / "Frame_bg_big_and_title.png"
        up_arrow_img_path = self.resources_base_path / "UI" / "Arrow_up.png"
        down_arrow_img_path = self.resources_base_path / "UI" / "Arrow_down.png"
        inventory_img_path = self.resources_base_path / "UI" / "Inventory_bg.png"
        slot_img_path = self.resources_base_path / "UI" / "Icon_Frame.png"

        # load images 
        shop_frame_img = pygame.image.load(shop_frame_img_path).convert_alpha()
        shop_inventory_img = pygame.image.load(inventory_img_path).convert_alpha()
        up_arrow_img = pygame.image.load(up_arrow_img_path).convert_alpha()
        down_arrow_img = pygame.image.load(down_arrow_img_path).convert_alpha()
        slot_img = pygame.image.load(slot_img_path).convert_alpha()

        # the img is 768 x 394. we're adding 32 pixels at the bottom for a 1 line text footer
        self.shop_base_surface = pygame.Surface((768, 426), pygame.SRCALPHA)
        self.shop_base_surface.fill((0, 0, 0, self.panel_alpha))

        self.shop_base_img = pygame.Surface((768, 426), pygame.SRCALPHA)

        # add the foundational frame to blank base surface 
        self.shop_base_img.blit(shop_frame_img, (0,0))

        # add 2 inventory screens
        self.shop_base_img.blit(shop_inventory_img, (30,40))
        self.shop_base_img.blit(shop_inventory_img, (505,40))

        # label the vendor's inventory screen
        vs_label = self.font.render("Vendor Stock", True, "grey87")
        self.shop_base_img.blit(vs_label, (35, 50))

        # label player's inventory screen
        yi_label = self.font.render("Your Inventory", True, "grey87")
        self.shop_base_img.blit(yi_label, (520,50))

        # apply the instructional footer
        footer = "Select    [Tab] Switch Inventory  [E]            [X] Close Shop"
        footer_fmt = self.font.render(footer, True, "grey87")
        self.shop_base_img.blit(footer_fmt, (45, 400))

        # up and down arrows
        self.shop_base_img.blit(up_arrow_img, (10,403))
        self.shop_base_img.blit(down_arrow_img, (25,403))

        # add vendor inventory slots
        for y in range(100, 350, 50):
            for x in range(36, 216, 44):
                self.shop_base_img.blit(slot_img, (x, y))

        # add player inventory slots
        for y in range(100, 350, 50):
            for x in range(511, 731, 44):
                self.shop_base_img.blit(slot_img, (x, y))

