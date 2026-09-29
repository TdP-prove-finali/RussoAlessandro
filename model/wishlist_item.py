from dataclasses import dataclass
from typing import Optional

from model.component import Component
from model.race import Race


@dataclass
class WishlistItem:
    item_id: int
    component: Component
    debut_race: Optional[Race] = None
    margin_days: Optional[int] = None
    value: Optional[float] = None
    production_cost: Optional[float] = None
    logistics_cost: Optional[float] = None
    transport_mode: Optional[str] = None
    transit_days: Optional[int] = None
    exclusion_label: Optional[str] = None

    def reset_results(self):
        self.debut_race = None
        self.margin_days = None
        self.value = None
        self.production_cost = None
        self.logistics_cost = None
        self.transport_mode = None
        self.transit_days = None
        self.exclusion_label = None

    def get_cost(self):
        if self.production_cost is None or self.logistics_cost is None:
            return None
        return self.production_cost + self.logistics_cost

    def get_roi(self):
        cost = self.get_cost()
        if self.value is None or not cost:
            return None
        return self.value / cost

    def __hash__(self):
        return hash(self.item_id)

    def __eq__(self, other):
        return isinstance(other, WishlistItem) and self.item_id == other.item_id

    def __str__(self):
        return str(self.component)
