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

    def get_bundle(self, index: int) -> SlotContent:
        # Return a valid slot's bundle, or None when that slot is currently empty.
        if index > self.num_slots - 1 or index < 0:
            raise IndexError(f"index {index} out of range for this Inventory's # of slots ({self.num_slots}).")
        else:
            return self._slots[index]

    @property
    def slots(self) -> tuple[SlotContent, ...]:
        # Expose slot contents for rendering without allowing callers to replace the
        # inventory's internal slot list.
        return tuple(self._slots)

        


            

        
