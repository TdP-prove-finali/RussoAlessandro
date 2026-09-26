from dataclasses import dataclass


@dataclass
class Component:
    component_id: int
    package_size: str
    focus: str
    base_gain_s: float
    cost_mln: float
    base_lead_time_days: int

    def __hash__(self):
        return hash(self.component_id)

    def __eq__(self, other):
        return isinstance(other, Component) and self.component_id == other.component_id

    def __str__(self):
        return f"{self.package_size} {self.focus}"
