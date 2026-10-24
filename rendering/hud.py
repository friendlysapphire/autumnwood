import pygame      

from characters.character import Character

def draw_player_status(player: Character, screen: pygame.Surface, font: pygame.font.Font) -> None:

    # Keep the always-visible status text readable over terrain of any color.
    status_background = pygame.Surface((190, 52), pygame.SRCALPHA)
    status_background.fill((0, 0, 0, 145))
    screen.blit(status_background, (7, 7))

    status_message_str = f"Health: {player.current_health}/{player.max_health}"  
    status_msg_fonted = font.render(status_message_str, True, (210, 180, 90))
    status_msg_fonted.set_alpha(220)
    screen.blit(status_msg_fonted, (15, 15))

    status_message_str = f"Gold: {player.gold_pieces}"  
    status_msg_fonted = font.render(status_message_str, True, (210, 180, 90))
    status_msg_fonted.set_alpha(220)
    screen.blit(status_msg_fonted, (15, 15 + font.get_linesize()))

   
