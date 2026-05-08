from __future__ import annotations

from forge.core.db import ForgeDB
from forge.core.models import CodeChange, CodebaseHealth, EvolutionRun, EvolutionTask


def test_task_round_trip() -> None:
    task = EvolutionTask(task_type="refactor", target="x.py", description="d", rationale="r")
    assert EvolutionTask.from_dict(task.to_dict()).id == task.id


def test_change_round_trip() -> None:
    change = CodeChange(task_id="t", diff="diff", files_changed=["x.py"])
    assert CodeChange.from_dict(change.to_dict()).files_changed == ["x.py"]


def test_run_round_trip() -> None:
    run = EvolutionRun(tasks_planned=2)
    assert EvolutionRun.from_dict(run.to_dict()).tasks_planned == 2


def test_health_round_trip() -> None:
    health = CodebaseHealth(overall_score=90, categories={"security": 90}, debt_items=[], trends={"security": "improving"})
    assert CodebaseHealth.from_dict(health.to_dict()).overall_score == 90


def test_db_init_and_add_task(tmp_path) -> None:
    db = ForgeDB(tmp_path)
    db.init()
    db.add_task(EvolutionTask(task_type="docs", target="README.md", description="d", rationale="r"))
    assert len(db.tasks()) == 1


def test_db_deduplicates_tasks(tmp_path) -> None:
    db = ForgeDB(tmp_path)
    task = EvolutionTask(task_type="docs", target="README.md", description="d", rationale="r")
    db.add_tasks([task, task])
    assert len(db.tasks()) == 1
