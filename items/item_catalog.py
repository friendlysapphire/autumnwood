from items.item import Item
from items.item_icon_paths import ICON_PATHS_BY_ITEM_ID
from items.item_id import ItemId


# The first real Autumnwood items. ItemId and ICON_PATHS_BY_ITEM_ID catalog every
# available source image, while this file deliberately lists only items the game
# currently recognizes as actual content.

APPLE = Item(
    id=ItemId.APPLE,
    display_name="Apple",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.APPLE],
    default_gold_value=2,
)

MUSHROOM = Item(
    id=ItemId.MUSHROOM,
    display_name="Mushroom",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.MUSHROOM],
    default_gold_value=3,
)

MEAT = Item(
    id=ItemId.MEAT,
    display_name="Meat",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.MEAT],
    default_gold_value=8,
)

WATER = Item(
    id=ItemId.WATER,
    display_name="Water",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.WATER],
    default_gold_value=2,
)

HEALTH_POTION = Item(
    id=ItemId.POTION_12,
    display_name="Health Potion",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.POTION_12],
    default_gold_value=20,
)

MANA_POTION = Item(
    id=ItemId.MANA_POTION_19,
    display_name="Mana Potion",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.MANA_POTION_19],
    default_gold_value=25,
)

BANDAGE = Item(
    id=ItemId.BANDAGE,
    display_name="Bandage",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.BANDAGE],
    default_gold_value=6,
)

TORCH = Item(
    id=ItemId.TORCH,
    display_name="Torch",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.TORCH],
    default_gold_value=4,
)

CANDLE = Item(
    id=ItemId.CANDLE,
    display_name="Candle",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.CANDLE],
    default_gold_value=2,
)

ROPE = Item(
    id=ItemId.ROPE,
    display_name="Rope",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.ROPE],
    default_gold_value=10,
)

WOOD = Item(
    id=ItemId.WOOD,
    display_name="Wood",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.WOOD],
    default_gold_value=1,
)

STONE = Item(
    id=ItemId.STONE,
    display_name="Stone",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.STONE],
    default_gold_value=1,
)

SPADE = Item(
    id=ItemId.SPADE,
    display_name="Spade",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.SPADE],
    default_gold_value=18,
)

PICK = Item(
    id=ItemId.PICK,
    display_name="Pick",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.PICK],
    default_gold_value=24,
)

IRON_SWORD = Item(
    id=ItemId.SWORD_38,
    display_name="Iron Sword",
    icon_path=ICON_PATHS_BY_ITEM_ID[ItemId.SWORD_38],
    default_gold_value=60,
)


# Use this when code has an ItemId but needs the corresponding Item object.
ITEMS_BY_ID: dict[ItemId, Item] = {
    APPLE.id: APPLE,
    MUSHROOM.id: MUSHROOM,
    MEAT.id: MEAT,
    WATER.id: WATER,
    HEALTH_POTION.id: HEALTH_POTION,
    MANA_POTION.id: MANA_POTION,
    BANDAGE.id: BANDAGE,
    TORCH.id: TORCH,
    CANDLE.id: CANDLE,
    ROPE.id: ROPE,
    WOOD.id: WOOD,
    STONE.id: STONE,
    SPADE.id: SPADE,
    PICK.id: PICK,
    IRON_SWORD.id: IRON_SWORD,
}
