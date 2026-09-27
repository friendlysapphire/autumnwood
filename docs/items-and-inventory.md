# Items and Inventory

Use this guide when adding an actual game item, creating starting stock, or
working with an inventory. The current system is deliberately a small
foundation for shop stock and future player items; it does not yet implement
equipment, consumable effects, gold, or buy/sell transactions.

## Item data flow

```text
ItemId
-> item_icon_paths
-> Item in item_catalog
-> ItemBundle with a current quantity
-> Inventory slot
```

The files have separate responsibilities:

| File | Responsibility |
|---|---|
| `items/item_id.py` | Stable internal identities for available item art. |
| `items/item_icon_paths.py` | Maps an `ItemId` to its DarkPixelUI source image. |
| `items/item.py` | Defines the immutable `Item` data shape: ID, display name, icon, base gold value, and per-bundle limit. |
| `items/item_catalog.py` | Defines actual Autumnwood items such as `APPLE` and exposes `ITEMS_BY_ID`. Not every available source image is an actual game item. |
| `items/item_bundle.py` | Represents one mutable quantity of one `Item`. |
| `items/inventory.py` | Stores and moves item bundles between fixed inventory slots. |

An `Item` is the shared fact sheet for a kind of item. An `ItemBundle` is a
particular changing pile, such as twelve Apples owned by a vendor. Never use
one shared mutable `ItemBundle` as stock for multiple vendors or inventories.

## Item icons

`Item` stores an authored `icon_path` and exposes `icon_surface` as a lazy
cached property. The first code that reads `item.icon_surface` loads the PNG
and runs `convert_alpha()`; later reads reuse that same Pygame `Surface` for
the rest of the game run.

Do not load the image in `Item.__post_init__()`. The item catalog imports
before Pygame creates its display, while `convert_alpha()` requires the display
to exist. Shop rendering accesses `icon_surface` only after display setup, so
it is the appropriate time to load and cache the image.

## Add an actual game item

The source art catalog is intentionally broader than the current game-item
catalog. Adding an image to `ItemId` and `item_icon_paths.py` makes that art
available; it does not automatically make it a real Autumnwood item.

To add a real item:

1. Ensure the required `ItemId` and icon-path entry exist.
2. Add a named `Item` object to `items/item_catalog.py` with its display name
   and base gold value.
3. Add that item to `ITEMS_BY_ID`.
4. Use that `Item` when creating an `ItemBundle` for stock, pickups, or a
   future reward.

## Inventory rules

`Inventory` owns a fixed-capacity internal list of `ItemBundle | None` slots.
After construction, its `_slots` list always contains exactly `num_slots`
entries. Empty slots are represented by `None`, so callers use the known slot
capacity rather than checking the list length.

The current behavior is:

- `add_item(item, quantity)` first fills compatible existing bundles, then
  uses empty slots. It returns the quantity that could not fit; `0` means the
  whole request fit.
- `remove_from_slot(index, quantity)` removes an exact quantity from the
  selected slot. It raises for an empty slot, a non-positive quantity, or a
  request larger than that bundle contains.
- Removing a bundle's final item replaces that slot with `None`.
- Empty slots may remain between occupied slots. Automatic compaction is not
  active, so removing an item does not shift the player's visible layout.

The current shop UI uses 25 slots in a five-by-five grid, but `Inventory`
accepts a configurable capacity up to the current `MAX_SLOTS` limit.

## Player and vendor ownership

Every `Character` owns an `Inventory`. Constructing a character without one
creates an empty inventory for it. A character can instead receive a prepared
inventory through its constructor.

`characters/npc_inventories.py` contains stock factories for NPCs. The current
`create_default_traveling_vendor_inventory()` factory creates a fresh
inventory for every traveling vendor loaded by `GameMap`.

```text
player Character
-> empty Inventory

traveling vendor NPC
-> fresh default Inventory

ShopPanel
-> temporarily references the player and vendor while the shop is open
```

The panel does not own either inventory. It will display and later coordinate
interaction with their contents.

## Current shop limits

The shop panel currently draws its static frame and tracks the 25 visual slot
rectangles for each side. The next implementation steps are rendering item
icons and quantities, visual selection, keyboard navigation, prices/gold, and
buy/sell transactions.
