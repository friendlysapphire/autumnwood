from dataclasses import dataclass

from items.item import Item

@dataclass
class ItemBundle:

    item: Item
    quantity: int
