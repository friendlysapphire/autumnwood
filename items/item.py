from dataclasses import dataclass
from pathlib import Path

from items.item_id import ItemId

@dataclass(frozen=True)
class Item:

    id: ItemId 
    display_name: str
    icon_path: Path
    
    # sellers may have different markups, this is the base value
    default_gold_value: int

    # max ItemBundle size (max size per inventory slot)
    max_bundle_qty: int = 10000
