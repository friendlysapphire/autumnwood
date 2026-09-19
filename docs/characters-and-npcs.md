# Characters and NPCs

Use this guide to place an existing NPC, add a new NPC type, or author the
linear dialogue currently supported by Autumnwood.

## Place an existing NPC in Tiled

Create a point object on the `NPCs` layer. The point represents the NPC's
initial feet-center placement.

Give it these values:

| Tiled field/property | Purpose |
|---|---|
| built-in Name | Internal runtime identity. Use a unique, stable name such as `traveling_vendor_01`. It can select a custom dialogue override. |
| `character_type` | Required. Selects the NPC type and scaffold. The current supported value is `traveling_vendor`. |
| `display_name` | Required player-facing name shown in the dialogue panel. |
| `spawn_on_map_load` | Optional boolean. Defaults to `true`; set it to `false` for an NPC a future trigger will spawn. |

The loader raises a map-authoring error when `display_name` is missing or
`character_type` is not recognized.

## Dialogue for an existing NPC type

NPC interaction content lives in `characters/npc_interactions.py` as immutable
`NPCInteractionDefinition` objects. `GameMap` resolves an interaction while it
loads the NPC, then the NPC keeps that resolved definition as
`interaction_definition`.

The lookup order is:

```text
exact interaction definition registered for the NPC's Tiled Name
-> default interaction definition registered for the NPCType
```

Use the default registry for ordinary NPCs of a type. For example, two
traveling vendors can have different internal Names and display names while
sharing the `TRAVELING_VENDOR` default dialogue.

Add an exact-name entry only when one NPC needs custom dialogue. Its key
must match the NPC's built-in Tiled Name exactly.

## Current dialogue limits

The dialogue panel is intentionally linear for now.

- `E` advances display pages and closes after the final page.
- `X` closes the conversation early.
- Movement is paused while dialogue is active.
- The panel has one speaker-name row and seven body rows. Statements are
  automatically wrapped and split into additional pages as needed.
- Author-chosen newline characters are preserved. Use them when a particular
  line break matters; otherwise author normal paragraph text and let the panel
  wrap it.
- `...` at the end of a page means the same authored statement continues on
  the next page.
- Until wrapping uses font pixel measurements, avoid an individual word wider
  than the panel's current character limit; it raises an explicit error.

Dialogue choices, shops, inventory, and branching conversations are future
work. Do not add a generic dialogue engine before those features have a
concrete use.

## Add a new NPC type

The current loader deliberately maps each supported NPC type explicitly.
To introduce a new type:

1. Add the new string value to `characters/npc_type.py`.
2. Add a `CharacterScaffold` in `characters/character_scaffolds.py` with
   the sprite path, animation rectangles, collision box, visible bounds,
   spawn offsets, and default speed measured for that asset.
3. Add the corresponding `NPCType` branch in `GameMap._load_map_elements()`
   to choose the scaffold and the initial interaction/spawn configuration.
4. If the loader configures that type as interactable, add its default
   interaction definition. Otherwise configure it as non-interactable for now.
5. Place a point object in Tiled using the new `character_type` and test
   its placement, collision, interaction range, and dialogue.

NPC collision and interaction rectangles can be inspected with the game's
backquote debug overlay.

For shared character/scaffold concepts and system ownership, see the
[Design Overview](design-overview.md).
