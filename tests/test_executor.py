from __future__ import annotations

from forge.core.db import ForgeDB
from forge.core.models import EvolutionTask
from forge.executor.executor import EvolutionExecutor
from forge.executor.patcher import PatchApplier
from forge.executor.test_runner import TestRunner


def test_patcher_updates_dependency(demo_root) -> None:
    task = EvolutionTask(task_type="dependency", target="requirements.txt", description="d", rationale="r")
    change = PatchApplier().apply(demo_root, task)
    assert "2.31.0" in (demo_root / "requirements.txt").read_text()
    assert change.status == "applied"


def test_patcher_fixes_sql(demo_root) -> None:
    task = EvolutionTask(task_type="security", target="app/data.py", description="d", rationale="r")
    PatchApplier().apply(demo_root, task)
    assert "WHERE name = ?" in (demo_root / "app/data.py").read_text()


def test_test_runner_passes_demo_tests(demo_root) -> None:
    passed, _ = TestRunner().run(demo_root)
    assert passed


def test_executor_completes_planned_task(demo_root) -> None:
    db = ForgeDB(demo_root)
    db.add_task(EvolutionTask(task_type="security", target="app/data.py", description="d", rationale="r"))
    run = EvolutionExecutor(db).execute(demo_root)
    assert run.tasks_completed == 1
    assert db.tasks()[0].status == "completed"


def test_executor_records_learning(demo_root) -> None:
    db = ForgeDB(demo_root)
    db.add_task(EvolutionTask(task_type="dependency", target="requirements.txt", description="d", rationale="r"))
    EvolutionExecutor(db).execute(demo_root)
    assert db.learning()[0]["success"] is True
