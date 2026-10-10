from enum import StrEnum
from pathlib import Path

import pygame

from characters.character import Character
from characters.npcs import NPC

from items.inventory import SlotContent

class ShopPanelSide(StrEnum):
    NPC = "npc"
    PLAYER = "player"

# TODO: lot of hard coded values in here that will need updates if we ever change the window size or
# make it user modifiable

class ShopPanel:

    def __init__(self,
                 *,
                 screen: pygame.Surface,
                 clock: pygame.Clock,
                 resources_base_path: Path,
                 window_height: int,
                 window_width: int,
                 alpha:int = 180,
                 header_font: pygame.font.Font | None = None,
                 ) -> None:

        self.resources_base_path = resources_base_path
        self.clock = clock

        self.window_height = window_height
        self.window_width = window_width
        self.panel_alpha = alpha
        self.screen = screen

        self.shop_active = False
        self.current_page_index:int = 0

        self.npc_shopkeeper: NPC | None = None
        self.player: Character | None = None

        self.player_slot_rects: list[pygame.Rect] = []
        self.npc_slot_rects: list[pygame.Rect] = []

        self.selected_slot = 0
        self.selected_side = ShopPanelSide.NPC
        # Both inventories share a five-by-five layout, so one index identifies the
        # selected position on either side of the shop.

        # TODO: there are at least 2 mor fonts in use now, call this "header font" or something and 
        # maybe remove entirely from the constructor
        if header_font is None:
            self.header_font = pygame.font.Font(None, 22)
        else:
            self.header_font = header_font

        self.quantity_font = pygame.font.Font(None,16)
        self.description_font = pygame.font.Font(None,18)

        # build a base image w/ all the static components of the shop panel so draw() can 
        # focus on the dynamic bits
        # this fn also inits self.player_slot_rects and self.npc_slot_rects
        self._init_shop_panel()

    # Run the paused shop screen until the player closes it. Shop navigation and
    # transaction controls will live in this local event loop as the screen grows.
    def run_modal(self,
                  background_image: pygame.Surface,
                  frames_per_second: int,
                  npc: NPC,
                  player: Character
                  ) -> None:

        self._open(npc, player)

        while True:

            # delay fps
            self.clock.tick(frames_per_second)

            self._draw(background_image)

            for event in pygame.event.get():

                match event.type:

                    case pygame.QUIT:
                        pygame.quit()
                        raise SystemExit

                    case pygame.KEYDOWN:

                        # Convert the flat slot index into grid coordinates so left and right wrap
                        # within the current row instead of moving into a different row.
                        row, col = divmod(self.selected_slot, 5)

                        match event.key:

                            # X closes the shop and returns control to normal gameplay.
                            case pygame.K_x:
                                self._close()
                                return

                            case pygame.K_RIGHT:
                                self.selected_slot = (row * 5) + (col + 1) % 5

                            case pygame.K_LEFT:
                                self.selected_slot = (row * 5) + (col - 1) % 5

                            case pygame.K_DOWN:
                                self.selected_slot = (self.selected_slot + 5) % 25

                            case pygame.K_UP:
                                self.selected_slot = (self.selected_slot - 5) % 25

                            # Start at a predictable valid slot after changing which inventory has focus.
                            case pygame.K_TAB:
                                if self.selected_side == ShopPanelSide.NPC:
                                    self.selected_side = ShopPanelSide.PLAYER
                                else:
                                    self.selected_side = ShopPanelSide.NPC

                                self.selected_slot = 0

    def _open(self, npc: NPC, player: Character) -> None:

        if self.shop_active is True:
            raise RuntimeError("Shop is already active, can't open another one.")
        
        else:
            self.shop_active = True
            self.current_page_index = 0
            self.npc_shopkeeper = npc
            self.player = player
            self.selected_slot = 0
            self.selected_side = ShopPanelSide.NPC

    def _close(self) -> None:
        self.shop_active = False
        self.current_page_index = 0
        self.npc_shopkeeper = None
        self.player = None
        self.selected_slot = 0
        self.selected_side = ShopPanelSide.NPC


    def _draw(self, background_image: pygame.Surface) -> None:
        if self.shop_active:

            # Restore the frozen world frame before drawing this shop-modal frame over it.
            self.screen.blit(background_image)

            # Clear the previous 
            self.shop_base_surface.fill((0, 0, 0, self.panel_alpha))

            # lay down the basic, static structure
            self.shop_base_surface.blit(self.shop_base_img, (0,0))

            # add vendor's displayname
            display_name = self.header_font.render(self.npc_shopkeeper.display_name, True, "grey87")
            self.shop_base_surface.blit(display_name, (25,10))

            # TODO: still needs cleanup. no action is avail if there's nothing in the slot
            footer = "Buy" if self.selected_side == ShopPanelSide.NPC else "Sell"

            footer_fmt = self.header_font.render(footer, True, "grey87")
            self.shop_base_surface.blit(footer_fmt, (315, 400))

            self._blit_player_inventory_to_base()
            self._blit_npc_inventory_to_base()

            # Select the matching panel-local rect so the gold outline follows the active
            # inventory while reusing the same slot index.
            if self.selected_side == ShopPanelSide.PLAYER:
                selected_slot_rect = self.player_slot_rects[self.selected_slot]
            else:
                selected_slot_rect = self.npc_slot_rects[self.selected_slot]

            pygame.draw.rect(
                self.shop_base_surface,
                "gold",
                selected_slot_rect,
                width=2,
                )
 
            # Display details for the same active-side slot marked by the gold outline.
            bundle = (
                self.player.inventory.slots[self.selected_slot]
                if self.selected_side == ShopPanelSide.PLAYER
                else self.npc_shopkeeper.inventory.slots[self.selected_slot]
            )

            if bundle is not None:
                # item icom
                icon_rect = bundle.item.icon_surface.get_rect(center=(384, 116))
                self.shop_base_surface.blit(bundle.item.icon_surface, icon_rect)

                # item name
                name = self.description_font.render(bundle.item.display_name, True, "grey87")
                self.shop_base_surface.blit(name, name.get_rect(midtop=(384, 150)))

                # item price
                if self.selected_side == ShopPanelSide.NPC:
                    price = self.description_font.render(f"Price per item: {self.npc_shopkeeper.get_stock_price(bundle.item)} gold.",
                                                         True,
                                                         "grey87")

                else:
                    price = self.description_font.render(f"Buyback Price per item: {self.npc_shopkeeper.get_buyback_price(bundle.item)} gold.",
                                                         True,
                                                         "grey87")
                
                self.shop_base_surface.blit(price, price.get_rect(midtop=(384, 170)))

                # item description
                desc = self.description_font.render(bundle.item.description, True, "grey87")
                self.shop_base_surface.blit(desc, (257, 200))

                # display player gold
                gold_display_txt = f"Player gold: {self.player.gold_pieces}"
                gold_display = self.header_font.render(gold_display_txt, True, "grey87")
                self.shop_base_surface.blit(gold_display, (20, 360))
            
            self.screen.blit(self.shop_base_surface, (96,123))

            pygame.display.flip()

    # INTERNAL ONLY HELPERS

    # initializes and blits shop panel + sets up attributes:
    # self.npc_slot_rects and self.player_slot_rects
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
        self.shop_base_img.blit(shop_inventory_img, (15,40))
        self.shop_base_img.blit(shop_inventory_img, (520,40))

        # label player's inventory screen
        vs_label = self.header_font.render("Your Inventory", True, "grey87")
        self.shop_base_img.blit(vs_label, (30, 50))

        # label vendor's inventory screen
        yi_label = self.header_font.render("Vendor Stock", True, "grey87")
        self.shop_base_img.blit(yi_label, (535,50))

        # apply the instructional footer
        footer = "Select    [Tab] Switch Inventory  [E]            [X] Close Shop"
        footer_fmt = self.header_font.render(footer, True, "grey87")
        self.shop_base_img.blit(footer_fmt, (45, 400))

        # up and down arrows
        self.shop_base_img.blit(up_arrow_img, (10,403))
        self.shop_base_img.blit(down_arrow_img, (25,403))

        # draw npc vendor and player inventory slots and set up internal structs

        slot_width, slot_height = slot_img.get_size()

        # player inventory slots
        for y in range(100, 350, 50):
            for x in range(21, 201, 44):
                slot_rect = pygame.Rect(x,y,slot_width, slot_height)
                self.shop_base_img.blit(slot_img, slot_rect)
                self.player_slot_rects.append(slot_rect)


        # npc inventory slots
        for y in range(100, 350, 50):
            for x in range(526, 746, 44):
                slot_rect = pygame.Rect(x,y,slot_width, slot_height)
                self.shop_base_img.blit(slot_img, slot_rect)
                self.npc_slot_rects.append(slot_rect)


    # Draw the player's current bundles into the player-side inventory grid.
    def _blit_player_inventory_to_base(self) -> None:
        self._blit_char_inventory_to_base(self.player.inventory.slots, self.player_slot_rects)

    # Draw the current shopkeeper's stock into the vendor-side inventory grid.
    def _blit_npc_inventory_to_base(self) -> None:
        self._blit_char_inventory_to_base(self.npc_shopkeeper.inventory.slots, self.npc_slot_rects)

    # This panel has 25 visual slots per side. Keep its slot rectangles and layout in
    # sync before increasing the inventory capacity beyond what the panel can render.
    # Pair each bundle with its matching panel-local slot rectangle and draw nonempty
    # bundles centered in their frames.
    def _blit_char_inventory_to_base(self, bundles: tuple[SlotContent, ...], slot_rects: list[pygame.Rect]) -> None:
        for bundle, slot_rect in zip(bundles, slot_rects):
            if bundle is not None:
                icon_rect = bundle.item.icon_surface.get_rect(center=slot_rect.center)
                self.shop_base_surface.blit(bundle.item.icon_surface, icon_rect)

                # add quantity
                if bundle.quantity > 0:
                    quantity_surface = self.quantity_font.render(str(bundle.quantity), True, "grey87")
                    quantity_rect = quantity_surface.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    self.shop_base_surface.blit(quantity_surface, quantity_rect)
