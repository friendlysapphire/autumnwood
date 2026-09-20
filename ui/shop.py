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

        #TODO: this is probably not how we should be locating the resources. figure out a better way
        self.shop_frame_img_path = self.resources_base_path / "UI" / "Frame_bg_big_and_title.png"
        self.up_arrow_img_path = self.resources_base_path / "UI" / "Arrow_up.png"
        self.down_arrow_img_path = self.resources_base_path / "UI" / "Arrow_down.png"
        self.inventory_img_path = self.resources_base_path / "UI" / "Inventory_bg.png"


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

        # the img is 768 x 394. we're adding 32 pixels at the bottom for a 1 line text footer
        self.shop_base_surface = pygame.Surface((768, 426), pygame.SRCALPHA)
        self.shop_base_surface.fill((0, 0, 0, self.panel_alpha))

        self.shop_frame_img = pygame.image.load(self.shop_frame_img_path).convert_alpha()
        self.shop_inventory_img = pygame.image.load(self.inventory_img_path).convert_alpha()

        self.up_arrow_img = pygame.image.load(self.up_arrow_img_path).convert_alpha()
        self.down_arrow_img = pygame.image.load(self.down_arrow_img_path).convert_alpha()

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

            # add the foundational frame to blank base surface 
            self.shop_base_surface.blit(self.shop_frame_img, (0,0))

            # add 2 inventory screens
            self.shop_base_surface.blit(self.shop_inventory_img, (30,40))
            self.shop_base_surface.blit(self.shop_inventory_img, (505,40))

            # label the 2 inventory screens
            vs_label = self.font.render("Vendor Stock", True, "grey87")
            yi_label = self.font.render("Your Inventory", True, "grey87")
            self.shop_base_surface.blit(vs_label, (35, 50))
            self.shop_base_surface.blit(yi_label, (520,50))

            # add vendor's displayname
            display_name = self.font.render(self.npc_shopkeeper.display_name, True, "grey87")
            self.shop_base_surface.blit(display_name, (25,10))


            # apply the instructional footer
            # TODO: e should buy or sell based on which inventory we're in and footer should display
            # accordingly
            footer = "Select    [Tab] Switch Inventory  [E] Buy/Sell [fixme]    [X] Close Shop"
            footer_fmt = self.font.render(footer, True, "grey87")
            self.shop_base_surface.blit(footer_fmt, (45, 400))

            # up and down arrows
            self.shop_base_surface.blit(self.up_arrow_img, (10,403))
            self.shop_base_surface.blit(self.down_arrow_img, (25,403))


            # TODO: stop hardcoding these values so we can resize windows. 
            self.screen.blit(self.shop_base_surface, (96,123))