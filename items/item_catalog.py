from items.item import Item
from items.item_icon_paths import ICON_PATHS_BY_ITEM_ID
from items.item_id import ItemId


# This is the authored item catalog. The names and values are deliberately kept
# together here, while ICON_PATHS_BY_ITEM_ID remains the source of icon locations.
# Values are a first pass and can be rebalanced as real shop gameplay takes shape.
def _item(item_id: ItemId, display_name: str, default_gold_value: int) -> Item:
    return Item(
        id=item_id,
        display_name=display_name,
        icon_path=ICON_PATHS_BY_ITEM_ID[item_id],
        default_gold_value=default_gold_value,
    )


SCROLL = _item(ItemId.SCROLL, "Scroll", 15)
RING = _item(ItemId.RING, "Ring", 30)
TORCH = _item(ItemId.TORCH, "Torch", 4)
HELM_04 = _item(ItemId.HELM_04, "Helm", 55)
CHEST_05 = _item(ItemId.CHEST_05, "Chest Armor", 75)
PANTS_06 = _item(ItemId.PANTS_06, "Leggings", 50)
BOOTS_07 = _item(ItemId.BOOTS_07, "Boots", 40)
GREEN_GEM = _item(ItemId.GREEN_GEM, "Green Gem", 40)
BLUE_GEM = _item(ItemId.BLUE_GEM, "Blue Gem", 50)
PURPLE_GEM = _item(ItemId.PURPLE_GEM, "Purple Gem", 65)
CROSS = _item(ItemId.CROSS, "Cross", 30)
HEALTH_POTION = _item(ItemId.POTION_12, "Health Potion", 20)
NECK_13 = _item(ItemId.NECK_13, "Necklace", 40)
WATER = _item(ItemId.WATER, "Water", 2)
SILVER_RING = _item(ItemId.SILVER_RING, "Silver Ring", 60)
GOLD_RING = _item(ItemId.GOLD_RING, "Gold Ring", 100)
BOTTLE = _item(ItemId.BOTTLE, "Empty Bottle", 3)
BOTTLE_OF_POWER = _item(ItemId.BOTTLE_OF_POWER, "Bottle of Power", 30)
MANA_POTION = _item(ItemId.MANA_POTION_19, "Mana Potion", 25)
POTION_20 = _item(ItemId.POTION_20, "Potion", 25)
MANA_POTION_21 = _item(ItemId.MANA_POTION_21, "Mana Potion", 30)
POTION_22 = _item(ItemId.POTION_22, "Potion", 30)
MANA_POTION_23 = _item(ItemId.MANA_POTION_23, "Mana Potion", 35)
MUSHROOM = _item(ItemId.MUSHROOM, "Mushroom", 3)
MEAT = _item(ItemId.MEAT, "Meat", 8)
APPLE = _item(ItemId.APPLE, "Apple", 2)
SKULL = _item(ItemId.SKULL, "Skull", 10)
BAG_28 = _item(ItemId.BAG_28, "Small Bag", 12)
BAG_29 = _item(ItemId.BAG_29, "Large Bag", 20)
MACE = _item(ItemId.MACE, "Mace", 65)
SPADE = _item(ItemId.SPADE, "Spade", 18)
COIN = _item(ItemId.COIN, "Gold Coin", 1)
STONE = _item(ItemId.STONE, "Stone", 1)
WOOD = _item(ItemId.WOOD, "Wood", 1)
GLOVES_35 = _item(ItemId.GLOVES_35, "Gloves", 25)
BOOK = _item(ItemId.BOOK, "Book", 20)
LEAF = _item(ItemId.LEAF, "Leaf", 1)
IRON_SWORD = _item(ItemId.SWORD_38, "Iron Sword", 60)
SWORD_39 = _item(ItemId.SWORD_39, "Sword", 75)
BOW = _item(ItemId.BOW, "Bow", 55)
ARROW = _item(ItemId.ARROW, "Arrow", 2)
SHIELD_42 = _item(ItemId.SHIELD_42, "Shield", 50)
SHIELD_43 = _item(ItemId.SHIELD_43, "Shield", 65)
ROPE = _item(ItemId.ROPE, "Rope", 10)
CRYSTAL = _item(ItemId.CRYSTAL, "Crystal", 35)
SKIN = _item(ItemId.SKIN, "Animal Hide", 8)
TREASURE = _item(ItemId.TREASURE, "Treasure Chest", 200)
BOOTS_48 = _item(ItemId.BOOTS_48, "Boots", 50)
PICK = _item(ItemId.PICK, "Pick", 24)
HELM_50 = _item(ItemId.HELM_50, "Helm", 65)
PANTS_51 = _item(ItemId.PANTS_51, "Leggings", 60)
CHEST_52 = _item(ItemId.CHEST_52, "Chest Armor", 90)
AXE = _item(ItemId.AXE, "Axe", 70)
SILVER_BAR = _item(ItemId.SILVER_BAR, "Silver Bar", 50)
FLOWER = _item(ItemId.FLOWER, "Flower", 2)
HELM_56 = _item(ItemId.HELM_56, "Helm", 80)
CHEST_57 = _item(ItemId.CHEST_57, "Chest Armor", 110)
BOOTS_58 = _item(ItemId.BOOTS_58, "Boots", 60)
PANTS_59 = _item(ItemId.PANTS_59, "Leggings", 70)
GLOVES_60 = _item(ItemId.GLOVES_60, "Gloves", 35)
POTION_61 = _item(ItemId.POTION_61, "Potion", 35)
POTION_62 = _item(ItemId.POTION_62, "Potion", 40)
STAIRWAY = _item(ItemId.STAIRWAY, "Stairway", 100)
CANDLE = _item(ItemId.CANDLE, "Candle", 2)
RED_CRYSTALS = _item(ItemId.RED_CRYSTALS, "Red Crystals", 50)
WAND = _item(ItemId.WAND, "Wand", 70)
BANDAGE = _item(ItemId.BANDAGE, "Bandage", 6)
RELIC = _item(ItemId.RELIC, "Relic", 150)
MAGIC_69 = _item(ItemId.MAGIC_69, "Magic Item", 60)
MAGIC_70 = _item(ItemId.MAGIC_70, "Magic Item", 70)
MAGIC_71 = _item(ItemId.MAGIC_71, "Magic Item", 80)
MAGIC_72 = _item(ItemId.MAGIC_72, "Magic Item", 90)
EQUIPMENT_BELT = _item(ItemId.EQUIPMENT_BELT, "Belt", 30)
EQUIPMENT_BRACELET = _item(ItemId.EQUIPMENT_BRACELET, "Bracelet", 35)
EQUIPMENT_CHEST = _item(ItemId.EQUIPMENT_CHEST, "Chest Armor", 80)
EQUIPMENT_GLOVES = _item(ItemId.EQUIPMENT_GLOVES, "Gloves", 30)
EQUIPMENT_HEAD = _item(ItemId.EQUIPMENT_HEAD, "Headgear", 50)
EQUIPMENT_JEWELRY = _item(ItemId.EQUIPMENT_JEWELRY, "Jewelry", 45)
EQUIPMENT_SHIELD = _item(ItemId.EQUIPMENT_SHIELD, "Shield", 60)
EQUIPMENT_SHOULDER = _item(ItemId.EQUIPMENT_SHOULDER, "Shoulder Armor", 55)
EQUIPMENT_TABARD = _item(ItemId.EQUIPMENT_TABARD, "Tabard", 45)
EQUIPMENT_TRINKET = _item(ItemId.EQUIPMENT_TRINKET, "Trinket", 40)
EQUIPMENT_WEAPON = _item(ItemId.EQUIPMENT_WEAPON, "Weapon", 75)
EQUIPMENT_ARROWS = _item(ItemId.EQUIPMENT_ARROWS, "Arrows", 10)
EQUIPMENT_BOOTS = _item(ItemId.EQUIPMENT_BOOTS, "Boots", 45)
EQUIPMENT_BOW = _item(ItemId.EQUIPMENT_BOW, "Bow", 65)
EQUIPMENT_NECK = _item(ItemId.EQUIPMENT_NECK, "Necklace", 45)
EQUIPMENT_PANTS = _item(ItemId.EQUIPMENT_PANTS, "Leggings", 55)
EQUIPMENT_RING = _item(ItemId.EQUIPMENT_RING, "Ring", 35)


# Keep the full item list in one readable order, then build the immutable lookup
# used by inventory, shops, and future map-item loading code.
ALL_ITEMS: tuple[Item, ...] = (
    SCROLL, RING, TORCH, HELM_04, CHEST_05, PANTS_06, BOOTS_07, GREEN_GEM,
    BLUE_GEM, PURPLE_GEM, CROSS, HEALTH_POTION, NECK_13, WATER, SILVER_RING,
    GOLD_RING, BOTTLE, BOTTLE_OF_POWER, MANA_POTION, POTION_20,
    MANA_POTION_21, POTION_22, MANA_POTION_23, MUSHROOM, MEAT, APPLE, SKULL,
    BAG_28, BAG_29, MACE, SPADE, COIN, STONE, WOOD, GLOVES_35, BOOK, LEAF,
    IRON_SWORD, SWORD_39, BOW, ARROW, SHIELD_42, SHIELD_43, ROPE, CRYSTAL,
    SKIN, TREASURE, BOOTS_48, PICK, HELM_50, PANTS_51, CHEST_52, AXE,
    SILVER_BAR, FLOWER, HELM_56, CHEST_57, BOOTS_58, PANTS_59, GLOVES_60,
    POTION_61, POTION_62, STAIRWAY, CANDLE, RED_CRYSTALS, WAND, BANDAGE,
    RELIC, MAGIC_69, MAGIC_70, MAGIC_71, MAGIC_72, EQUIPMENT_BELT,
    EQUIPMENT_BRACELET, EQUIPMENT_CHEST, EQUIPMENT_GLOVES, EQUIPMENT_HEAD,
    EQUIPMENT_JEWELRY, EQUIPMENT_SHIELD, EQUIPMENT_SHOULDER,
    EQUIPMENT_TABARD, EQUIPMENT_TRINKET, EQUIPMENT_WEAPON, EQUIPMENT_ARROWS,
    EQUIPMENT_BOOTS, EQUIPMENT_BOW, EQUIPMENT_NECK, EQUIPMENT_PANTS,
    EQUIPMENT_RING,
)


# Use this when code has an ItemId but needs the corresponding Item object.
ITEMS_BY_ID: frozendict[ItemId, Item] = frozendict({
    item.id: item
    for item in ALL_ITEMS
})
