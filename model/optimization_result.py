from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OptimizationResult:
    included_items: list = field(default_factory=list)
    excluded_items: list = field(default_factory=list)
    total_value: float = 0.0
    total_cost: float = 0.0
    max_value: float = 0.0
    phase1_cost: float = 0.0
    performance_price: Optional[float] = None
    available_budget: float = 0.0
    phase1_seconds: float = 0.0
    phase2_seconds: float = 0.0
    total_seconds: float = 0.0

    def get_savings(self):
        return self.phase1_cost - self.total_cost

    def get_performance_loss_pct(self):
        if self.max_value <= 0:
            return 0.0
        return (self.max_value - self.total_value) / self.max_value * 100

    def get_committed_budget(self):
        return self.total_cost

    def get_remaining_budget(self):
        return self.available_budget - self.total_cost

    def get_roi(self):
        if self.total_cost <= 0:
            return None
        return self.total_value / self.total_cost
