from dataclasses import dataclass
from enum import StrEnum

import pygame

from characters.npcs import NPC

# DialogPanel owns active conversation state and renders the currently selected
# statement from the speaking NPC's dialogue script.
class DialogPanel:

    def __init__(self,
                 *,
                 screen: pygame.Surface,
                 panel_width:int,
                 panel_height:int,
                 window_height: int,
                 window_width: int,
                 alpha:int = 180,
                 font: pygame.font.Font | None = None
                 ) -> None:
        
        self.panel_width = panel_width
        self.panel_height = panel_height
        self.window_height = window_height
        self.window_width = window_width
        self.panel_alpha = alpha
        self.screen = screen

        self.dialog_active: bool = False
        self.current_dialog_index:int = 0
        self.speaking_npc: NPC | None = None

        if font is None:
            self.font = pygame.font.Font(None, 22)
        else:
            self.font = font

        # This transparent Surface is redrawn only while an active dialogue exists.
        self.dialog_panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.dialog_panel.fill((0, 0, 0, self.panel_alpha))

    def start_dialog(self, speaking_npc: NPC) -> None:
        # Every new conversation begins at its first statement, including when the
        # player speaks to the same NPC again.
        self.dialog_active = True
        self.current_dialog_index = 0
        self.speaking_npc = speaking_npc
        self.draw()

    def advance_dialog(self) -> None:

        if self.dialog_active is False:
            raise RuntimeError(f"There is no current dialog to advance.")

        max_index = len(self.speaking_npc.dialog_info.statements) - 1

        if self.current_dialog_index < max_index:
            self.current_dialog_index += 1
        else:
            self.clear_dialog()

    def clear_dialog(self) -> None:
        self.dialog_active = False
        self.current_dialog_index = 0
        self.speaking_npc = None

    # Draw the active dialogue's header, fixed-size body area, and footer for this frame.
    def draw(self) -> None:

        if self.dialog_active:
            # Clear the previous dialogue text before drawing the active statement.
            self.dialog_panel.fill((0, 0, 0, self.panel_alpha))

            # prepare text string for the panel
            
            # header is NPC's displayname
            text = self.speaking_npc.display_name + "\n"

            # Reserve seven body rows so the footer remains anchored at the bottom of
            # the panel regardless of the current statement's length.
            text += self.speaking_npc.dialog_info.statements[self.current_dialog_index]

            num_newlines = text.count('\n')
            if num_newlines > 7:
                # Statements exceeding seven body rows will need pagination; automatic
                # wrapping and paging are intentionally deferred from this first version.
                raise NotImplementedError(f"NPC {self.speaking_npc.display_name}'s dialog has too"
                                          " many newlines; paging not yet implemented.")

            newlines_to_add = 7 - num_newlines
            text += "\n" * newlines_to_add

            # footer 
            text += "\n[X] End Conversation [E] Continue Conversation"

            dialog_surface = self.font.render(text, True, "grey87")
            self.dialog_panel.blit(dialog_surface, (10,10))
            self.screen.blit(self.dialog_panel, (20, (self.window_height - self.panel_height) - 5))
