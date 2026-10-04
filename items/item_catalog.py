from items.item import Item
from items.item_icon_paths import ICON_PATHS_BY_ITEM_ID
from items.item_id import ItemId


# This is the authored item catalog. The names and values are deliberately kept
# together here, while ICON_PATHS_BY_ITEM_ID remains the source of icon locations.
# Values are a first pass and can be rebalanced as real shop gameplay takes shape.
# Require a description for every authored catalog entry so shop items cannot
# silently fall back to blank player-facing text.
def _item(item_id: ItemId, display_name: str, default_gold_value: int, description: str) -> Item:
    return Item(
        id=item_id,
        display_name=display_name,
        icon_path=ICON_PATHS_BY_ITEM_ID[item_id],
        default_gold_value=default_gold_value,
        description=description,
    )


SCROLL = _item(ItemId.SCROLL, "Scroll", 15, "A rolled sheet of mysterious writing.")
RING = _item(ItemId.RING, "Ring", 30, "A simple ring for a willing finger.")
TORCH = _item(ItemId.TORCH, "Torch", 4, "A wooden torch for dark places.")
HELM_04 = _item(ItemId.HELM_04, "Helm", 55, "A basic metal helmet.")
CHEST_05 = _item(ItemId.CHEST_05, "Chest Armor", 75, "A suit of sturdy chest armor.")
PANTS_06 = _item(ItemId.PANTS_06, "Leggings", 50, "Protective armor for your legs.")
BOOTS_07 = _item(ItemId.BOOTS_07, "Boots", 40, "Tough boots for long journeys.")
GREEN_GEM = _item(ItemId.GREEN_GEM, "Green Gem", 40, "A polished green gemstone.")
BLUE_GEM = _item(ItemId.BLUE_GEM, "Blue Gem", 50, "A polished blue gemstone.")
PURPLE_GEM = _item(ItemId.PURPLE_GEM, "Purple Gem", 65, "A polished purple gemstone.")
CROSS = _item(ItemId.CROSS, "Cross", 30, "A simple symbol of faith.")
HEALTH_POTION = _item(ItemId.POTION_12, "Health Potion", 20, "A red potion that restores health.")
NECK_13 = _item(ItemId.NECK_13, "Necklace", 40, "A simple necklace for daily wear.")
WATER = _item(ItemId.WATER, "Water", 2, "Clean water in a small container.")
SILVER_RING = _item(ItemId.SILVER_RING, "Silver Ring", 60, "A polished silver ring.")
GOLD_RING = _item(ItemId.GOLD_RING, "Gold Ring", 100, "A polished gold ring.")
BOTTLE = _item(ItemId.BOTTLE, "Empty Bottle", 3, "An empty bottle for useful liquids.")
BOTTLE_OF_POWER = _item(ItemId.BOTTLE_OF_POWER, "Bottle of Power", 30, "A bottle filled with strange power.")
MANA_POTION = _item(ItemId.MANA_POTION_19, "Mana Potion", 25, "A blue potion that restores mana.")
POTION_20 = _item(ItemId.POTION_20, "Potion", 25, "A bottle of unknown liquid.")
MANA_POTION_21 = _item(ItemId.MANA_POTION_21, "Mana Potion", 30, "A stronger blue restorative potion.")
POTION_22 = _item(ItemId.POTION_22, "Potion", 30, "A larger bottle of unknown liquid.")
MANA_POTION_23 = _item(ItemId.MANA_POTION_23, "Mana Potion", 35, "A powerful blue restorative potion.")
MUSHROOM = _item(ItemId.MUSHROOM, "Mushroom", 3, "An edible mushroom from the wild.")
MEAT = _item(ItemId.MEAT, "Meat", 8, "A portion of fresh meat.")
APPLE = _item(ItemId.APPLE, "Apple", 2, "A crisp apple for a quick snack.")
SKULL = _item(ItemId.SKULL, "Skull", 10, "A weathered skull of unknown origin.")
BAG_28 = _item(ItemId.BAG_28, "Small Bag", 12, "A small bag for carrying supplies.")
BAG_29 = _item(ItemId.BAG_29, "Large Bag", 20, "A large bag for carrying supplies.")
MACE = _item(ItemId.MACE, "Mace", 65, "A heavy weapon with a metal head.")
SPADE = _item(ItemId.SPADE, "Spade", 18, "A small tool for digging earth.")
COIN = _item(ItemId.COIN, "Gold Coin", 1, "A single gold coin.")
STONE = _item(ItemId.STONE, "Stone", 1, "A common stone.")
WOOD = _item(ItemId.WOOD, "Wood", 1, "A piece of useful lumber.")
GLOVES_35 = _item(ItemId.GLOVES_35, "Gloves", 25, "Sturdy gloves for working hands.")
BOOK = _item(ItemId.BOOK, "Book", 20, "A book filled with old knowledge.")
LEAF = _item(ItemId.LEAF, "Leaf", 1, "A leaf from a nearby plant.")
IRON_SWORD = _item(ItemId.SWORD_38, "Iron Sword", 60, "A dependable sword of iron.")
SWORD_39 = _item(ItemId.SWORD_39, "Sword", 75, "A well-made sword for close combat.")
BOW = _item(ItemId.BOW, "Bow", 55, "A wooden bow for ranged attacks.")
ARROW = _item(ItemId.ARROW, "Arrow", 2, "A single arrow for a bow.")
SHIELD_42 = _item(ItemId.SHIELD_42, "Shield", 50, "A sturdy shield for defense.")
SHIELD_43 = _item(ItemId.SHIELD_43, "Shield", 65, "A reinforced shield for defense.")
ROPE = _item(ItemId.ROPE, "Rope", 10, "A coil of strong rope.")
CRYSTAL = _item(ItemId.CRYSTAL, "Crystal", 35, "A clear crystal with a faint shine.")
SKIN = _item(ItemId.SKIN, "Animal Hide", 8, "A cured hide from a wild animal.")
TREASURE = _item(ItemId.TREASURE, "Treasure Chest", 200, "A chest filled with valuable treasure.")
BOOTS_48 = _item(ItemId.BOOTS_48, "Boots", 50, "Well-made boots for rough ground.")
PICK = _item(ItemId.PICK, "Pick", 24, "A tool for breaking stone.")
HELM_50 = _item(ItemId.HELM_50, "Helm", 65, "A reinforced metal helmet.")
PANTS_51 = _item(ItemId.PANTS_51, "Leggings", 60, "Reinforced armor for your legs.")
CHEST_52 = _item(ItemId.CHEST_52, "Chest Armor", 90, "Reinforced armor for your chest.")
AXE = _item(ItemId.AXE, "Axe", 70, "A sharp axe for heavy work.")
SILVER_BAR = _item(ItemId.SILVER_BAR, "Silver Bar", 50, "A refined bar of silver.")
FLOWER = _item(ItemId.FLOWER, "Flower", 2, "A bright flower from the wild.")
HELM_56 = _item(ItemId.HELM_56, "Helm", 80, "A finely made metal helmet.")
CHEST_57 = _item(ItemId.CHEST_57, "Chest Armor", 110, "A finely made suit of chest armor.")
BOOTS_58 = _item(ItemId.BOOTS_58, "Boots", 60, "Fine boots for rough journeys.")
PANTS_59 = _item(ItemId.PANTS_59, "Leggings", 70, "Fine armor for your legs.")
GLOVES_60 = _item(ItemId.GLOVES_60, "Gloves", 35, "Fine gloves for careful work.")
POTION_61 = _item(ItemId.POTION_61, "Potion", 35, "A carefully brewed potion.")
POTION_62 = _item(ItemId.POTION_62, "Potion", 40, "A potent bottle of unknown liquid.")
STAIRWAY = _item(ItemId.STAIRWAY, "Stairway", 100, "A carved stairway of unknown use.")
CANDLE = _item(ItemId.CANDLE, "Candle", 2, "A small candle with a warm flame.")
RED_CRYSTALS = _item(ItemId.RED_CRYSTALS, "Red Crystals", 50, "A cluster of glowing red crystals.")
WAND = _item(ItemId.WAND, "Wand", 70, "A wooden wand with a magical focus.")
BANDAGE = _item(ItemId.BANDAGE, "Bandage", 6, "Clean cloth for treating small wounds.")
RELIC = _item(ItemId.RELIC, "Relic", 150, "An ancient relic of unknown purpose.")
MAGIC_69 = _item(ItemId.MAGIC_69, "Magic Item", 60, "A strange object humming with magic.")
MAGIC_70 = _item(ItemId.MAGIC_70, "Magic Item", 70, "A curious object touched by magic.")
MAGIC_71 = _item(ItemId.MAGIC_71, "Magic Item", 80, "A rare object filled with magic.")
MAGIC_72 = _item(ItemId.MAGIC_72, "Magic Item", 90, "A powerful object steeped in magic.")
EQUIPMENT_BELT = _item(ItemId.EQUIPMENT_BELT, "Belt", 30, "A plain belt for carrying gear.")
EQUIPMENT_BRACELET = _item(ItemId.EQUIPMENT_BRACELET, "Bracelet", 35, "A simple bracelet for the wrist.")
EQUIPMENT_CHEST = _item(ItemId.EQUIPMENT_CHEST, "Chest Armor", 80, "A protective piece of chest armor.")
EQUIPMENT_GLOVES = _item(ItemId.EQUIPMENT_GLOVES, "Gloves", 30, "Plain gloves for everyday work.")
EQUIPMENT_HEAD = _item(ItemId.EQUIPMENT_HEAD, "Headgear", 50, "Protective gear for the head.")
EQUIPMENT_JEWELRY = _item(ItemId.EQUIPMENT_JEWELRY, "Jewelry", 45, "A small piece of decorative jewelry.")
EQUIPMENT_SHIELD = _item(ItemId.EQUIPMENT_SHIELD, "Shield", 60, "A shield made for steady defense.")
EQUIPMENT_SHOULDER = _item(ItemId.EQUIPMENT_SHOULDER, "Shoulder Armor", 55, "Armor made to protect the shoulders.")
EQUIPMENT_TABARD = _item(ItemId.EQUIPMENT_TABARD, "Tabard", 45, "A cloth tabard worn over armor.")
EQUIPMENT_TRINKET = _item(ItemId.EQUIPMENT_TRINKET, "Trinket", 40, "A small trinket with personal value.")
EQUIPMENT_WEAPON = _item(ItemId.EQUIPMENT_WEAPON, "Weapon", 75, "A weapon ready for the next fight.")
EQUIPMENT_ARROWS = _item(ItemId.EQUIPMENT_ARROWS, "Arrows", 10, "A bundle of arrows for a bow.")
EQUIPMENT_BOOTS = _item(ItemId.EQUIPMENT_BOOTS, "Boots", 45, "Practical boots for everyday travel.")
EQUIPMENT_BOW = _item(ItemId.EQUIPMENT_BOW, "Bow", 65, "A bow built for careful aim.")
EQUIPMENT_NECK = _item(ItemId.EQUIPMENT_NECK, "Necklace", 45, "A necklace with a simple charm.")
EQUIPMENT_PANTS = _item(ItemId.EQUIPMENT_PANTS, "Leggings", 55, "Practical leggings for travel.")
EQUIPMENT_RING = _item(ItemId.EQUIPMENT_RING, "Ring", 35, "A plain ring with a soft shine.")


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
