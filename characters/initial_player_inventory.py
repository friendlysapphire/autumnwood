from items.inventory import Inventory
from items.item_bundle import ItemBundle
from items import item_catalog


# Build fresh mutable stock for new player
# Each call creates independent ItemBundles, so vendors never share stock after trades.
def create_default_player_inventory() -> Inventory:
    return Inventory(initial_inventory=[
        ItemBundle(item=item_catalog.APPLE, quantity=5),
        ItemBundle(item=item_catalog.WATER, quantity=20),
        ItemBundle(item=item_catalog.HEALTH_POTION, quantity=6),
        ItemBundle(item=item_catalog.BANDAGE, quantity=30),
    ])