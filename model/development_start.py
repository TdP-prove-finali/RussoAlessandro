import datetime
from dataclasses import dataclass


@dataclass
class DevelopmentStart:
    date: datetime.date

    def __hash__(self):
        return hash(self.date)

    def __eq__(self, other):
        return isinstance(other, DevelopmentStart) and self.date == other.date

    def __str__(self):
        return f"Development start ({self.date})"
