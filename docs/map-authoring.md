# Map Authoring

Use this guide when creating or editing an Autumnwood map in Tiled. It
describes the current authoring contract; Python loads gameplay metadata
only from the named object layers below.

## Start from the desert template

`resources/autumnwood_desert_template.tmx` contains the current Epic RPG
desert tilesets and a useful layer layout. Copy it before authoring a new
desert map. `autumnwood_desert_starter.tmx` is a smaller painted example.

Tiled's visible tile-layer order is the draw order. Keep lower terrain
layers below scenery.

## Paint visible map art

The visual layers are map art only; painting a tree or water tile does not
create collision or gameplay behavior by itself.

- `Ground` holds base terrain.
- `Terrain` and `Water`, when present in a template, hold additional terrain art.
- `walls` is intentionally lowercase because the Epic RPG World Automapping
  rules target that exact layer name.
- `Scenery` holds complete props such as trees, rocks, tents, and houses.

Keep complete props on `Scenery`. Add separate object-layer metadata only
when Python needs to reason about the prop.

## Add gameplay metadata

Layer names are case-sensitive. Create or use these Tiled object layers as
needed:

| Layer | Authoring purpose |
|---|---|
| `Collisions` | Rectangles the player cannot enter. No properties required. |
| `Spawns` | Named point objects such as `player_start` and transition destinations. |
| `Regions` | Special rectangular gameplay areas. See [Regions and Region Effects](regions-and-region-effects.md). |
| `World Objects` | Invisible interaction rectangles for discrete static objects. |
| `NPCs` | Point objects for map-authored NPCs. See [Characters and NPCs](characters-and-npcs.md). |

`World Objects`, `NPCs`, and `Regions` are not substitutes for scenery art.
For example, paint an apple tree on `Scenery`, then add an appropriately
placed rectangle on `World Objects` when it should be interactable.

## Add player and transition spawns

Place a point object on `Spawns` and set its built-in Tiled Name. The map
currently needs a `player_start` point for its initial player placement.
Map-transition regions refer to destination spawn Names, not coordinates.

## Before testing

- Check that visible props are on visual tile layers, not object layers.
- Add collision rectangles for scenery that should block movement.
- Ensure every required object-layer property is spelled exactly as its
  corresponding guide specifies.
- Use the backquote debug toggle in the game to inspect loaded collision,
  region, World Object, and NPC rectangles.

For the overall separation between map art and runtime objects, see the
[Design Overview](design-overview.md).
