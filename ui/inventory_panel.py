import textwrap

from pathlib import Path

import pygame

from characters.character import Character
from characters.npcs import NPC

from items.item_bundle import ItemBundle
from items.inventory import SlotContent
from items.item_use import use_item, item_has_action, ITEM_USE_PRESENT_TENSE
from rendering.hud import draw_player_status


# TODO: lot of hard coded values in here that will need updates if we ever change the window size or
# make it user modifiable

class PlayerInventoryPanel:

    def __init__(self,
                 *,
                 screen: pygame.Surface,
                 clock: pygame.Clock,
                 resources_base_path: Path,
                 window_height: int,
                 window_width: int,
                 alpha:int = 180,
                 player: Character,
                 header_font: pygame.font.Font | None = None,
                 ) -> None:

        self.resources_base_path = resources_base_path
        self.resources_base_sprites_path = self.resources_base_path / "spritepacks" / "DarkPixelUI"

        self.clock = clock

        self.window_height = window_height
        self.window_width = window_width
        self.panel_alpha = alpha
        self.screen = screen

        self.panel_active = False
        self.current_page_index:int = 0

        self.player: Character = player

        self.player_slot_rects: list[pygame.Rect] = []

        self.selected_slot = 0

        if header_font is None:
            self.header_font = pygame.font.Font(None, 22)
        else:
            self.header_font = header_font

        self.quantity_font = pygame.font.Font(None,16)
        self.description_font = pygame.font.Font(None,18)

        self.temporary_message: str | None = None

        # build a base image w/ all the static components of the inventory panel so draw()
        # can focus on the dynamic bits
        # this fn also inits self.player_slot_rects
        self._init_inventory_panel()

    # Run the paused player inventory screen until the player closes it.
    def run_modal(self,
                  background_image: pygame.Surface,
                  frames_per_second: int
                  ) -> None:

        self._open()

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

                            # X closes the inventory and returns control to normal gameplay.
                            case pygame.K_x:
                                self._close()
                                return

                            # Clear the previous use message when moving to another slot.
                            case pygame.K_RIGHT:
                                self.selected_slot = (row * 5) + (col + 1) % 5
                                self.temporary_message = None

                            case pygame.K_LEFT:
                                self.selected_slot = (row * 5) + (col - 1) % 5
                                self.temporary_message = None

                            case pygame.K_DOWN:
                                self.selected_slot = (self.selected_slot + 5) % 25
                                self.temporary_message = None

                            case pygame.K_UP:
                                self.selected_slot = (self.selected_slot - 5) % 25
                                self.temporary_message = None

                            case pygame.K_e:
                                # Use the same action lookup as the footer so E does nothing for an empty
                                # slot or an item with no available action.
                                bundle = self.player.inventory.get_bundle(self.selected_slot)
                                if bundle is not None and item_has_action(bundle.item) is True:
                                    self.temporary_message = "You "
                                    self.temporary_message += use_item(self.player,self.selected_slot)
                                    
    def _open(self) -> None:

        if self.panel_active is True:
            raise RuntimeError("Player inventory panel is already active, can't open another one.")
        
        else:
            self.panel_active = True
            self.current_page_index = 0
            self.selected_slot = 0
            self.temporary_message = None

    def _close(self) -> None:
        self.panel_active = False
        self.current_page_index = 0
        self.selected_slot = 0
        self.temporary_message = None

    def _get_selected_bundle(self) -> ItemBundle | None:
            return self.player.inventory.slots[self.selected_slot]

    def _draw(self, background_image: pygame.Surface) -> None:
        if self.panel_active:

            # Restore the frozen world frame before drawing the inventory panel over it.
            self.screen.blit(background_image)

            # sneakily update the hud health/gold status
            draw_player_status(self.player, self.screen)

            # Clear the previous frame's dynamic panel contents before rebuilding it.
            self.panel_base_surface.fill((0, 0, 0, self.panel_alpha))

            # lay down the basic, static structure
            self.panel_base_surface.blit(self.panel_base_img, (0,0))

            self._blit_player_inventory_to_base()

            selected_slot_rect = self.player_slot_rects[self.selected_slot]

            pygame.draw.rect(
                self.panel_base_surface,
                "gold",
                selected_slot_rect,
                width=2,
                )

            # display the current temporary message, if there is one
            if self.temporary_message is not None:
                tmp_msg = self.header_font.render(self.temporary_message, True, "gold1")
                self.panel_base_surface.blit(tmp_msg, (35, 435))

            # display player gold
            gold_display_txt = f"Player gold: {self.player.gold_pieces}"
            gold_display = self.header_font.render(gold_display_txt, True, "grey87")
            self.panel_base_surface.blit(gold_display, (282, 370))
 
            # Display details for the slot marked by the gold outline.
            bundle = self._get_selected_bundle()

            if bundle is not None:
                # item icon
                icon_rect = bundle.item.icon_surface.get_rect(center=(390, 135))
                self.panel_base_surface.blit(bundle.item.icon_surface, icon_rect)

                # item name
                name = self.description_font.render(bundle.item.display_name, True, "grey87")
                self.panel_base_surface.blit(name, name.get_rect(midtop=(390, 175)))

                # item description
                string_list = textwrap.wrap(bundle.item.description, width=30)
                line_height = self.description_font.get_linesize()

                for index, desc_str in enumerate(string_list):
                    # max 6 lines, then just cut it off.
                    if index == 6:
                        break
                    desc = self.description_font.render(desc_str, True, "grey87")
                    self.panel_base_surface.blit(desc, (282, 210 + (index * line_height)))

                # if item is usable, show the [E] <appopriate verb> text
                if item_has_action(bundle.item) is True:
                    action_verb = bundle.item.action_words[ITEM_USE_PRESENT_TENSE]
                    footer = f"[E] {action_verb[0].upper() + action_verb[1:]}"
                    footer_fmt = self.header_font.render(footer, True, "grey87")
                    self.panel_base_surface.blit(footer_fmt, (344, 470))
        
            # Slot coordinates above are panel-local; center the completed panel in the window.
            panel_rect = self.panel_base_surface.get_rect(center=self.screen.get_rect().center)

            self.screen.blit(self.panel_base_surface, panel_rect)

            pygame.display.flip()

    # initializes the inventory panel and sets up self.player_slot_rects
    def _init_inventory_panel(self) -> None:

        panel_frame_img_path = self.resources_base_sprites_path / "UI" / "Frame_square_512.png"
        title_frame_img_path = self.resources_base_sprites_path / "UI" / "Title_frame_m.png"
        slot_img_path = self.resources_base_sprites_path / "UI" / "Icon_Frame.png"
        bag_img_path = self.resources_base_sprites_path / "UI" / "BAR_Bag.png"

        # load images 
        panel_frame_img = pygame.image.load(panel_frame_img_path).convert_alpha()
        title_frame_img = pygame.image.load(title_frame_img_path).convert_alpha()
        slot_img = pygame.image.load(slot_img_path).convert_alpha()
        bag_img = pygame.image.load(bag_img_path).convert_alpha()

        # Working surface for the current frame. draw() clears it, copies the static
        # artwork onto it, then adds the changing inventory contents.
        self.panel_base_surface = pygame.Surface((512,512), pygame.SRCALPHA)
        self.panel_base_surface.fill((0, 0, 0, self.panel_alpha))

        # Compose the static panel artwork once and reuse it when rebuilding each frame.
        self.panel_base_img = pygame.Surface((512,512), pygame.SRCALPHA)

        # add the foundational frame to blank base surface 
        self.panel_base_img.blit(panel_frame_img, (0,0))

        # add the title frame
        self.panel_base_img.blit(title_frame_img, (160,12))

        # "Inventory" title text
        title_text = self.header_font.render("Inventory", True, "grey87")
        title_rect = title_text.get_rect(midtop=(256, 25))
        self.panel_base_img.blit(title_text, title_rect)

        # bag
        self.panel_base_img.blit(bag_img, (12, 70))

        # "Your Inventory" title text
        inv_text = self.header_font.render("Your Inventory", True, "grey87")
        self.panel_base_img.blit(inv_text, (36, 90))

        # apply the instructional footer
        footer = "[Arrow Keys] Select  [X] Close Inventory"
        footer_fmt = self.header_font.render(footer, True, "grey87")
        self.panel_base_img.blit(footer_fmt, (35, 470))

        # draw player inventory slots and set up internal structs

        slot_width, slot_height = slot_img.get_size()

        # player inventory slots
        for y in range(128, 378, 50):
            for x in range(28, 248, 44):
                slot_rect = pygame.Rect(x,y,slot_width, slot_height)
                self.panel_base_img.blit(slot_img, slot_rect)
                self.player_slot_rects.append(slot_rect)

    # Draw the player's current bundles into the player-side inventory grid.
    def _blit_player_inventory_to_base(self) -> None:
        self._blit_char_inventory_to_base(self.player.inventory.slots, self.player_slot_rects)

    # This panel has 25 visual slots. Keep its slot rectangles and layout in
    # sync before increasing the inventory capacity beyond what the panel can render.
    # Pair each bundle with its matching panel-local slot rectangle and draw nonempty
    # bundles centered in their frames.
    def _blit_char_inventory_to_base(self, bundles: tuple[SlotContent, ...], slot_rects: list[pygame.Rect]) -> None:
        for bundle, slot_rect in zip(bundles, slot_rects):
            if bundle is not None:
                icon_rect = bundle.item.icon_surface.get_rect(center=slot_rect.center)
                self.panel_base_surface.blit(bundle.item.icon_surface, icon_rect)

                # add quantity
                if bundle.quantity > 0:
                    quantity_surface = self.quantity_font.render(str(bundle.quantity), True, "grey87")
                    quantity_rect = quantity_surface.get_rect(bottomright=(slot_rect.right - 2, slot_rect.bottom - 2))
                    self.panel_base_surface.blit(quantity_surface, quantity_rect)
