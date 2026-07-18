from pathlib import Path

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FRAMES_PER_SECOND = 60

PROJECT_ROOT = Path(__file__).parent
MAP_PATH = PROJECT_ROOT / "resources" / "testmap.tmx"


def get_player_start(tiled_map: pytmx.TiledMap) -> tuple[float, float]:

    for layer in tiled_map.layers:
        if isinstance(layer, pytmx.TiledObjectGroup):
            if layer.name == "Spawns":
                for obj in layer:
                    if obj.name == "player_start":
                        return (obj.x, obj.y)

    raise ValueError("Could not find initial player start location.")

def main() -> None:
    # Set up Pygame and create the game window.
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Xiao map test")
    clock = pygame.time.Clock()

    # Load the Tiled map and its referenced tile images.
    tiled_map = load_pygame(MAP_PATH)

    # get player start location
    start_x, start_y = get_player_start(tiled_map)

    print(f"starting at {start_x}, {start_y}")

    running = True

    while running:
        # Read pending window and input events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the previous frame before drawing the map again.
        screen.fill("black")

        # Draw each visible tile layer from bottom to top.
        for layer in tiled_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for tile_x, tile_y, tile_image in layer.tiles():
                    screen_x = tile_x * tiled_map.tilewidth
                    screen_y = tile_y * tiled_map.tileheight

                    screen.blit(tile_image, (screen_x, screen_y))

        # Make the completed frame visible, then limit loop speed.
        pygame.display.flip()
        clock.tick(FRAMES_PER_SECOND)

    pygame.quit()


if __name__ == "__main__":
    main()