from characters.character import Character
from items.action_words import ItemActionWords
from items.item import Item
from items.item_id import ItemId


ITEM_USE_PRESENT_TENSE = 0
ITEM_USE_PAST_TENSE = 1


# Call this when code only needs to know whether an item currently offers an
# action. Today that is determined by action_words; keeping the test here lets
# that rule change later without updating every caller.
def item_has_action(item: Item) -> bool:
    return get_item_action_words(item) is not None

# return a usage string for eg a player inventory view or similar. "eat" for apple, etc...
def get_item_action_words(item: Item) -> ItemActionWords | None:
    return item.action_words


# Shared healing-consumable flow: keep the item at full health, otherwise
# restore health, remove one item from the exact selected slot, and describe it.
# The supplied item must have action_words because the outcome uses them.
def restore_char_health_and_remove_item(
        character: Character,
        item: Item,
        slot_index: int,
        amount: int
        ) -> tuple[int, str]:

    item_name = item.display_name
    verb = item.action_words

    if character.is_at_full_health() is True:
        return (0,
                f"did not {verb[ITEM_USE_PRESENT_TENSE]} the {item_name}, already at full health.")
    else:
        # Choose "a" or "an" for the player-facing outcome message.
        particle = "an" if verb[ITEM_USE_PAST_TENSE][0] in ["a", "e", "i", "o", "u"] else "a"
        restored = character.restore_health(amount)
        # considered putting an assert restored isn't 0 here, but there could be a modifier
        # on the player diminishing healing or something to a value that ends up rounding to 0
        character.inventory.remove_from_slot(slot_index, quantity=1)
        return (restored, f"{verb[ITEM_USE_PAST_TENSE]} {particle} {item_name}, restoring {restored} health points.")


# for all inventory items that have any use ability (which i think would be any excepy something you're carrying 
# to give to someone or something), this holkd the logic to 'use'.
# 'use' could mean consume, wear, etc...
# Call only after item_has_action() confirms the item in this slot has an
# action, and don't change the slot between that check and this call.
# Returns a description of the outcome, intended to follow "You " in the UI.

def use_item(character: Character, slot_index: int) -> str:

    bundle = character.inventory.get_bundle(slot_index)
    
    if bundle is None:
        raise ValueError(f"{character.display_name} inventory slot {slot_index} has an empty bundle. Can't use item there.")

    if (qty := bundle.quantity) <= 0:
        raise ValueError(f"Unexpected item quantity of {qty} for {character.display_name}, {bundle.item.display_name}")

    match bundle.item.id:

        case ItemId.APPLE:
            _, s = restore_char_health_and_remove_item(character,
                                                       bundle.item,
                                                       slot_index,
                                                       5)
            return s
            
        case _:
            # user should not be able to 'use' a non-usable item. so this would be a logic error or an unimplemented
            # use (above). so this should throw.
            raise ValueError(f"{character.display_name} tried to use {bundle.item.display_name}, which can't be used.")
