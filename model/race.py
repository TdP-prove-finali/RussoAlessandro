import datetime
from dataclasses import dataclass


@dataclass
class Race:
    race_id: int
    season: int
    round: int
    race_name: str
    date: datetime.date
    is_sprint: bool
    circuit_id: str
    circuit_name: str
    locality: str
    country: str
    lat: float
    lng: float
    aero_index: float
    chassis_index: float
    power_index: float
    rain_prob: float

    def __hash__(self):
        return hash(self.race_id)

    def __eq__(self, other):
        return isinstance(other, Race) and self.race_id == other.race_id

    def __str__(self):
        return self.race_name
