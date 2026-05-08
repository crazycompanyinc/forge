from __future__ import annotations

from forge.core.models import EvolutionTask


class PriorityQueue:
    PRIORITY = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    RISK = {"safe": 0, "moderate": 1, "risky": 2}
    TYPE = {"security": 0, "test": 1, "dependency": 2, "performance": 3, "refactor": 4, "style": 5, "docs": 6, "feature": 7}

    def order(self, tasks: list[EvolutionTask]) -> list[EvolutionTask]:
        return sorted(tasks, key=lambda task: (self.PRIORITY[task.priority], self.RISK[task.estimated_risk], self.TYPE[task.task_type], task.target))
