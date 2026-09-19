from dataclasses import dataclass
from enum import StrEnum

import pygame

from characters.npcs import NPC

# DialogPanel owns active conversation state and renders the currently selected
# page from the speaking NPC's dialogue script.
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

        # This temporary character-count limit approximates the body width. Keep it below
        # the visible capacity so continuation pages can append "..." without re-wrapping.
        # Replace it with font/pixel measurement when dialogue needs proportional-font accuracy.
        self.max_chars = 105


        # The speaker header plus seven dialogue rows fit above the fixed footer.
        self.max_lines_above_footer = 8
        self.max_newline_chars_above_footer = self.max_lines_above_footer - 1


        self.dialog_active: bool = False
        self.current_page_index:int = 0
        self.speaking_npc: NPC | None = None
        # Runtime display pages generated from the speaking NPC's authored dialogue statements.
        self.dialogue_pages: list[str] | None = None

        if font is None:
            self.font = pygame.font.Font(None, 22)
        else:
            self.font = font

        # This transparent Surface is redrawn only while an active dialogue exists.
        self.dialog_panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        self.dialog_panel.fill((0, 0, 0, self.panel_alpha))

    def start_dialog(self, speaking_npc: NPC) -> None:
        # Every new conversation begins at its first page, including when the
        # player speaks to the same NPC again.
        self.dialog_active = True
        self.current_page_index = 0
        self.speaking_npc = speaking_npc
        self.dialogue_pages = []

        # Build wrapped runtime entries without changing the NPC’s authored dialogue script.
        wrapped_statements: list[str] = []
        for statement in self.speaking_npc.dialog_info.statements:
            wrapped_statements.append(self._wrap(statement))
        
        # Flatten wrapped statements into display pages while preserving conversation order.
        for wrapped_statement in wrapped_statements:
            self.dialogue_pages.extend(self._paginate(wrapped_statement, self.max_newline_chars_above_footer))

        self.draw()

    def advance_dialog(self) -> None:

        if self.dialog_active is False:
            raise RuntimeError(f"There is no current dialog to advance.")

        # Linear dialogue closes after its final page rather than advancing past it.
        max_index = len(self.dialogue_pages) - 1

        if self.current_page_index < max_index:
            self.current_page_index += 1
        else:
            self.clear_dialog()

    def clear_dialog(self) -> None:
        # Reset all conversation-specific state so the next interaction begins cleanly.
        self.dialog_active = False
        self.current_page_index = 0
        self.speaking_npc = None
        self.dialogue_pages = None

    # Draw the active dialogue panel after its current text layout has been composed.
    def draw(self) -> None:

        if self.dialog_active:
            # Clear the previous dialogue text before drawing the active page.
            self.dialog_panel.fill((0, 0, 0, self.panel_alpha))

            text: str = self._compose_dialogue_panel_text()

            dialog_surface = self.font.render(text, True, "grey87")
            self.dialog_panel.blit(dialog_surface, (10,10))
            self.screen.blit(self.dialog_panel, (20, (self.window_height - self.panel_height) - 5))

    # INTERNAL METHODS

    # Split a wrapped statement into page strings containing at most max_lines rendered rows.
    # Full pages ending before the statement does are marked with "..." (and assuming max_chars
    # gives us enough room to do this at any point w/o special casing or re-wrapping, ie max_chars is at least '...' less than
    # the max visible area)
    def _paginate(self, statement: str, max_lines: int) -> list[str]:

        paginated: list[str] = []

        # _wrap has already converted this statement into rendered rows separated by newlines.
        strs = statement.split('\n')

        if len(strs) <= max_lines:
            return [statement]

        else:

            # Build complete pages first; any remaining rows become one final partial page.
            full_pages = len(strs) // max_lines

            for _ in range(full_pages):
                page: list[str] = []
                for _ in range(max_lines):
                    page.append(strs.pop(0))

                if strs:
                    # Mark the final row when another page from this statement follows.
                    page[-1] += "..."

                paginated.append('\n'.join(page))

            if strs:
                # Append the remaining rows as the final partial page.
                paginated.append('\n'.join(strs))

        return paginated
                    

    # Pack words (space separated text units) into rendered rows that do not exceed the character limit.
    def _recompose(self, s: str) -> list[str]:

        final_list: list[str] = []

        # Consume words in order, starting a new row only when the next word will not fit.
        word_queue = s.split(' ')
        tmp: str = ""

        while word_queue:

            # this version does not hyphenate or split words. A later pixel-based
            # wrapper can decide how to handle an individual word wider than the panel.
            if len(word_queue[0]) > self.max_chars:
                raise NotImplementedError("NPC Dialog panel must be wider than the individual words you want to put there."
                                        "Increase dialoge panel width. Really, this should never happen.")
        
            else: 
                # tmp keeps a trailing space while a row is being assembled, so its
                # length includes the separator required before a following word.
                if len(word_queue[0]) + len(tmp) <= self.max_chars:
                    tmp += word_queue.pop(0) + " "
                else:
                    final_list.append(tmp.strip())
                    tmp = word_queue.pop(0) + " "

                if not word_queue and tmp:
                    # Flush the final row after consuming the last word.
                    final_list.append(tmp.strip())

        return final_list

    # TODO i have since discovered textwrap exists. 
    # Convert one authored statement into newline-separated rendered rows while preserving
    # author-chosen line breaks for later pagination.
    def _wrap(self, s: str) -> str:

        final_strs: list[str] = []

        # Preserve author-chosen newlines by wrapping each original row independently
        # before pagination.
        original_lines = s.split('\n')

        for line in original_lines:
            composed_str_list = self._recompose(line)
            final_strs.extend(composed_str_list)

        return '\n'.join(final_strs)

    # Build the current linear dialogue page: speaker header, paginated body text,
    # padding, and fixed E/X controls. Choice menus will need different composition.
    def _compose_dialogue_panel_text(self) -> str:
        
        text = self.speaking_npc.display_name + "\n"

        text += self.dialogue_pages[self.current_page_index]

        # The header contributes the first newline; pad to the configured limit so
        # the footer remains anchored below the dialogue body.
        num_newlines = text.count('\n')

        newlines_to_add = self.max_newline_chars_above_footer - num_newlines
        text += "\n" * newlines_to_add

        # Linear dialogue uses fixed E/X controls after padding. Choice menus will later
        # supply controls based on their current selection state.
        text += "\n[X] End Conversation     [E] Continue Conversation"

        return text
