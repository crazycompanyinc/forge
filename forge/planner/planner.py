from __future__ import annotations

from pathlib import Path

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.core.models import EvolutionRun, EvolutionTask
from forge.planner.generator import TaskGenerator
from forge.planner.priority import PriorityQueue


class EvolutionPlanner:
    def __init__(self) -> None:
        self.analyzer = CodebaseAnalyzer()
        self.generator = TaskGenerator()
        self.priority = PriorityQueue()

    def plan(self, path: str | Path = ".", task_type: str | None = None) -> tuple[EvolutionRun, list[EvolutionTask]]:
        health = self.analyzer.analyze(path)
        tasks = self.priority.order(self.generator.generate(health.debt_items, task_type))
        risk_map = {"safe": 0.15, "moderate": 0.45, "risky": 0.8}
        run = EvolutionRun(
            tasks_planned=len(tasks),
            overall_risk_score=round(sum(risk_map[t.estimated_risk] for t in tasks) / max(len(tasks), 1), 2),
            task_ids=[task.id for task in tasks],
        )
        return run, tasks
