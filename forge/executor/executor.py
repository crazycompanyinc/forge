from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from forge.core.db import ForgeDB
from forge.core.models import EvolutionRun, EvolutionTask
from forge.executor.patcher import PatchApplier
from forge.executor.test_runner import TestRunner
from forge.learning.success import SuccessTracker
from forge.verifier.rollback import RollbackManager


class EvolutionExecutor:
    def __init__(self, db: ForgeDB | None = None) -> None:
        self.db = db or ForgeDB()
        self.patcher = PatchApplier()
        self.tests = TestRunner()
        self.rollback = RollbackManager()
        self.success = SuccessTracker(self.db)

    def execute(self, path: str | Path = ".", task_id: str | None = None) -> EvolutionRun:
        root = Path(path)
        tasks = self.db.tasks("planned")
        if task_id:
            tasks = [task for task in self.db.tasks() if task.id == task_id and task.status in {"planned", "approved"}]
        run = EvolutionRun(tasks_planned=len(tasks), task_ids=[task.id for task in tasks])
        self.db.add_run(run)
        for task in tasks:
            self._execute_task(root, task, run)
        run.status = "completed" if run.tasks_failed == 0 else "failed"
        run.completed_at = datetime.now(timezone.utc).isoformat()
        return run

    def _execute_task(self, root: Path, task: EvolutionTask, run: EvolutionRun) -> None:
        snapshot = self.rollback.snapshot(root)
        task.status = "executing"
        self.db.update_task(task)
        try:
            change = self.patcher.apply(root, task)
            passed, output = self.tests.run(root)
            change.tests_passed = passed
            if passed:
                change.status = "verified"
                task.status = "completed"
                run.tasks_completed += 1
                self.success.record(task, True, "tests passed")
            else:
                self.rollback.restore(root, snapshot)
                change.status = "rolled_back"
                task.status = "rolled_back"
                run.tasks_failed += 1
                self.success.record(task, False, output[-1000:])
            self.db.add_change(change)
        except Exception as exc:
            self.rollback.restore(root, snapshot)
            task.status = "failed"
            run.tasks_failed += 1
            self.success.record(task, False, str(exc))
        finally:
            if task.status in {"completed", "failed", "rolled_back"}:
                task.completed_at = datetime.now(timezone.utc).isoformat()
            self.db.update_task(task)
