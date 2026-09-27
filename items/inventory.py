from items.item import Item
from items.item_bundle import ItemBundle
from typing import TypeAlias

# One inventory slot either holds an item bundle or is empty.
SlotContent: TypeAlias = ItemBundle | None

MAX_SLOTS = 25
DEFAULT_NUM_SLOTS = 25

# "slots" is available space for inventories, the upper bound of the inventory list
# After construction, _slots always contains exactly num_slots entries. Empty
# available slots are represented by None, so callers validate positions against
# num_slots rather than checking the list length.
class Inventory:

    def __init__(self,
                 num_slots: int = DEFAULT_NUM_SLOTS,
                 initial_inventory: list[SlotContent] | None = None
                 ):

        self._slots: list[SlotContent] = []

        if num_slots > MAX_SLOTS:
            raise ValueError("Can't construct Inventory. num_slots can't exceed: "
                                f"{MAX_SLOTS} (received {num_slots})")
        elif num_slots <= 0:
            raise ValueError("Can't construct Inventory. num_slots can't be <= 0: "
                            f"(received {num_slots})")

        else:
            self.num_slots = num_slots

        # Copy supplied slot contents, then pad empty positions until the inventory reaches
        # its fixed capacity.
        if initial_inventory is not None:

            if (num_inv_values := len(initial_inventory)) > MAX_SLOTS:
                raise ValueError(f"Inventory hard limit is {MAX_SLOTS} slots. Can't construct new Inventory"
                                   " with a longer initial list.")
            elif num_inv_values > num_slots:
                raise ValueError(f"You requested {self.num_slots} slots and provided {num_inv_values} slots."
                                 "Can't construct new Inventory under those conditions.")
            else:
                self._slots = list(initial_inventory)

        # pad out with None
        if (slots_len := len(self._slots)) < self.num_slots:
            for _ in range(slots_len, self.num_slots):
                self._slots.append(None)

        assert len(self._slots) == self.num_slots

    @property
    def slots(self) -> tuple[SlotContent, ...]:
        # Expose slot contents for rendering without allowing callers to replace the
        # inventory's internal slot list.
        return tuple(self._slots)

    # Return a valid slot's bundle, or None when that slot is currently empty.
    def get_bundle(self, index: int) -> SlotContent:
        self._range_check(index)
        return self._slots[index]

    # place a bundle (or None) at an index, replacing whatever was at that index and not shifting elements
    def place_bundle(self, bundle: SlotContent, index: int) -> None:
        self._range_check(index)
        self._slots[index] = bundle

    # Add as much of an item as this inventory can hold, returning any quantity that
    # could not fit into compatible bundles or empty slots.
    def add_item(self, item: Item, quantity: int) -> int:

        amt_left = quantity

        if quantity <= 0:
            raise ValueError(f"Can't add {quantity} quantity to an ItemBundle.")

        # First fill compatible existing bundles, stopping early once all quantity fits.
        # Then create new bundles in empty slots for any remaining quantity. Return any
        # quantity still left when no more slots are available.

        for index, slot in enumerate(self._slots):

            if slot is not None:
                # if we're looking at the right type of item and it's not already full
                if slot.item.id == item.id and slot.quantity < slot.item.max_bundle_qty:

                    amt_left = self._add_quantity_to_bundle(index, amt_left)
                    if amt_left == 0:
                        return amt_left

        # traverse again looking for None slots and fill tose up until we accommodate the new items or run out
        # of space.
        #

        for index, slot in enumerate(self._slots):

            if slot is None:
                # add a new empty bundle here of the correct type
                new_bundle = ItemBundle(item=item, quantity=0)
                self._slots[index] = new_bundle

                amt_left = self._add_quantity_to_bundle(index, amt_left)
                if amt_left == 0:
                    return amt_left

        return amt_left

    # Remove an exact quantity from the selected slot; the bundle already in that slot
    # determines which item is being removed.
    def remove_from_slot(self, index: int, quantity: int) -> None:
        self._subtract_quantity_from_bundle(index, quantity)

    # INTERNAL ONLY METHODS

    # returns overflow from bundle or 0 if all items added
    def _add_quantity_to_bundle(self, index: int, quantity: int = 1) -> int:

        overflow = 0 

        if quantity <= 0:
            raise ValueError(f"Can't add {quantity} quantity to an ItemBundle.")

        self._range_check(index)
        bundle: SlotContent = self._slots[index]

        if bundle is None:
            raise ValueError(f"Can't add quantity to an empty bundle slot (None)")

        elif (new_qty := bundle.quantity + quantity) > bundle.item.max_bundle_qty:
            bundle.quantity = bundle.item.max_bundle_qty
            overflow = new_qty - bundle.quantity   
        else:
            bundle.quantity = new_qty

        return overflow

    def _subtract_quantity_from_bundle(self, index: int, quantity: int = 1) -> None:

        if quantity <= 0:
            raise ValueError(f"Can't remove {quantity} quantity from an ItemBundle.")

        self._range_check(index)

        bundle: SlotContent = self._slots[index]

        if bundle is None:
            raise ValueError(f"Can't remove a quantity from an empty bundle slot (None)")

        # could have simplified this into a max(0,bundle.quantity - quantity) situation
        elif (new_qty := bundle.quantity - quantity) < 0:
            raise ValueError(f"Can't remove {quantity} from ItemBundle, would result in invalid {new_qty} items.")
        else:
            bundle.quantity = new_qty

        if bundle.quantity == 0:
            self._slots[index] = None

    def _range_check(self, index: int) -> None:
        if index < 0 or index > self.num_slots - 1:
            raise IndexError(f"index {index} out of range for this Inventory's # of slots ({self.num_slots}).")

    # currently unused but lurking in case we want to do this in the future
    
    # move all non-None bundles to the front of the list and pad out w/ Nones in the back 
    # (preserves order, gets rid of empty slots interspersed w/ full slots)
    def _compact_slots(self) -> None:
        new_slot_list = [slot for slot in self._slots if slot is not None]
        if (slots_len := len(new_slot_list)) < self.num_slots:
            for _ in range(slots_len, self.num_slots):
                new_slot_list.append(None)
        self._slots = new_slot_list

    
