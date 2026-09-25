from dataclasses import dataclass
from typing import Optional


@dataclass
class Constructor:
    constructor_id: str
    name: str
    nationality: str
    url: str
    base_city: str
    base_country: str
    base_lat: float
    base_lng: float
    first_season: int
    last_season: Optional[int]

    def __hash__(self):
        return hash(self.constructor_id)

    def __eq__(self, other):
        return isinstance(other, Constructor) and self.constructor_id == other.constructor_id

    def __str__(self):
        return self.name
