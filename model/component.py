from dataclasses import dataclass


@dataclass(frozen=True)
class Component:
    component_id: int
    package_size: str
    focus: str
    base_gain_s: float
    cost_mln: float
    base_lead_time_days: int

    def __str__(self):
        return f"{self.package_size} {self.focus}"
