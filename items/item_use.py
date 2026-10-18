from characters.character import Character
from items.item import Item
from items.item_id import ItemId


# return a usage string for eg a player inventory view or similar. "eat" for apple, etc...
# Keep these actions in sync with the cases handled by use_item().
def get_item_action(item: Item) -> str | None:
    
    match item.id:

        case ItemId.APPLE:
            return "Eat"

        case _:
            # items may not be 'usable' and if that's the case, return nothing.
            return None


# for all inventory items that have any use ability (which i think would be any excepy something you're carrying 
# to give to someone or something), this holkd the logic to 'use'.
# 'use' could mean consume, wear, etc...
# Call only after get_item_action() confirms the item in this slot has an
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
            # TODO use thie item -- increase player health or something
            # Consuming the apple removes one from the selected slot.
            character.inventory.remove_from_slot(slot_index, 1)
            return "ate an apple, restoring some vigor."
            
        case _:
            # user should not be able to 'use' a non-usable item. so this would be a logic error or an unimplemented
            # use (above). so this should throw.
            raise ValueError(f"{character.display_name} tried to use {bundle.item.display_name}, which can't be used.")
