from dataclasses import dataclass
from typing import Optional

from model.component import Component
from model.race import Race


@dataclass
class WishlistItem:
    item_id: int
    component: Component
    debut_race: Optional[Race] = None

    def __hash__(self):
        return hash(self.item_id)

    def __eq__(self, other):
        return isinstance(other, WishlistItem) and self.item_id == other.item_id

    def __str__(self):
        return str(self.component)
