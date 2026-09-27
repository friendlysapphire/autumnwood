from items.inventory import Inventory
from items.item_bundle import ItemBundle
from items import item_catalog


# Build fresh mutable stock for each newly created generic traveling vendor.
# Each call creates independent ItemBundles, so vendors never share stock after trades.
def create_default_traveling_vendor_inventory() -> Inventory:
    return Inventory(initial_inventory=[
        ItemBundle(item=item_catalog.APPLE, quantity=12),
        ItemBundle(item=item_catalog.MUSHROOM, quantity=8),
        ItemBundle(item=item_catalog.MEAT, quantity=4),
        ItemBundle(item=item_catalog.WATER, quantity=10),
        ItemBundle(item=item_catalog.HEALTH_POTION, quantity=5),
        ItemBundle(item=item_catalog.MANA_POTION, quantity=3),
        ItemBundle(item=item_catalog.BANDAGE, quantity=8),
        ItemBundle(item=item_catalog.TORCH, quantity=5),
        ItemBundle(item=item_catalog.CANDLE, quantity=12),
        ItemBundle(item=item_catalog.ROPE, quantity=3),
        ItemBundle(item=item_catalog.WOOD, quantity=20),
        ItemBundle(item=item_catalog.STONE, quantity=20),
        ItemBundle(item=item_catalog.SPADE, quantity=1),
        ItemBundle(item=item_catalog.PICK, quantity=1),
        ItemBundle(item=item_catalog.IRON_SWORD, quantity=1),
    ])
