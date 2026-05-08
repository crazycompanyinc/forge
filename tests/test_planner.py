from __future__ import annotations

from forge.planner.generator import TaskGenerator
from forge.planner.planner import EvolutionPlanner
from forge.planner.priority import PriorityQueue


def test_generator_creates_tasks_from_issues() -> None:
    tasks = TaskGenerator().generate([{"type": "security", "target": "x.py", "description": "bad", "severity": "critical"}])
    assert tasks[0].priority == "critical"


def test_generator_filters_type() -> None:
    tasks = TaskGenerator().generate(
        [
            {"type": "security", "target": "x.py", "description": "bad", "severity": "critical"},
            {"type": "docs", "target": "x.py", "description": "missing", "severity": "low"},
        ],
        "docs",
    )
    assert len(tasks) == 1
    assert tasks[0].task_type == "docs"


def test_priority_orders_security_first() -> None:
    tasks = TaskGenerator().generate(
        [
            {"type": "docs", "target": "x.py", "description": "missing", "severity": "low"},
            {"type": "security", "target": "x.py", "description": "bad", "severity": "critical"},
        ]
    )
    assert PriorityQueue().order(tasks)[0].task_type == "security"


def test_planner_creates_run(demo_root) -> None:
    run, tasks = EvolutionPlanner().plan(demo_root)
    assert run.tasks_planned == len(tasks)
    assert run.overall_risk_score > 0


def test_planner_type_specific(demo_root) -> None:
    _, tasks = EvolutionPlanner().plan(demo_root, "dependency")
    assert tasks
    assert all(task.task_type == "dependency" for task in tasks)
