from dataclasses import dataclass
from typing import Optional

from model.race import Race


@dataclass
class Shipment:
    race: Race
    mode: str
    distance_km: float
    travel_hours: Optional[float]
    transit_days: int
    logistics_cost: float
    estimated_route: bool = False

    def __str__(self):
        days = "day" if self.transit_days == 1 else "days"
        return f"{self.race}: {self.mode}, {self.distance_km:.0f} km, {self.transit_days} {days}"
