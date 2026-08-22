# Autumnwood

Autumnwood is a top-down 2D RPG I'm writing with my daughter, who is contributing the art, world design, and story ideas.

The project is also a way for me to rebuild my Python fluency while developing a real game incrementally rather than following isolated programming exercises.

## Technology

- Python
- Pygame-CE
- PyTMX
- Tiled

## Current Status

The game currently supports:

- tile-based maps created in Tiled
- animated player movement
- camera scrolling and map boundaries
- collision detection
- gameplay regions and region effects
- terrain-based movement effects such as quicksand
- transitions between maps using named spawn points
- debug visualization of regions and collision areas

The next major piece is the world-object and interaction system, followed by basic NPCs and dialogue.

## Documentation

More detailed design notes are in [`docs/`](docs/):

- [`design-overview.md`](docs/design-overview.md) — overview of the current game architecture
- [`regions-and-region-effects.md`](docs/regions-and-region-effects.md) — guide to the region/effect system and adding new region types

## Development

Autumnwood is a work in progress. The architecture is intentionally evolving alongside the gameplay rather than being designed completely up front.