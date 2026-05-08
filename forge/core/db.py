from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from forge.core.models import CodeChange, CodebaseHealth, EvolutionRun, EvolutionTask

T = TypeVar("T")


class ForgeDB:
    """Small JSON document store kept inside .forge/state.json."""

    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root)
        self.state_dir = self.root / ".forge"
        self.path = self.state_dir / "state.json"

    def init(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"tasks": [], "changes": [], "runs": [], "health": [], "learning": []})

    def load(self) -> dict[str, Any]:
        self.init()
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state: dict[str, Any]) -> None:
        self.init()
        self._write(state)

    def add_task(self, task: EvolutionTask) -> None:
        state = self.load()
        state["tasks"].append(task.to_dict())
        self.save(state)

    def add_tasks(self, tasks: list[EvolutionTask]) -> None:
        state = self.load()
        existing = {(task["task_type"], task["target"], task["description"]) for task in state["tasks"]}
        for task in tasks:
            key = (task.task_type, task.target, task.description)
            if key not in existing:
                state["tasks"].append(task.to_dict())
                existing.add(key)
        self.save(state)

    def tasks(self, status: str | None = None) -> list[EvolutionTask]:
        tasks = [EvolutionTask.from_dict(item) for item in self.load()["tasks"]]
        return [task for task in tasks if task.status == status] if status else tasks

    def update_task(self, task: EvolutionTask) -> None:
        state = self.load()
        state["tasks"] = [task.to_dict() if item["id"] == task.id else item for item in state["tasks"]]
        self.save(state)

    def add_change(self, change: CodeChange) -> None:
        state = self.load()
        state["changes"].append(change.to_dict())
        self.save(state)

    def changes(self) -> list[CodeChange]:
        return [CodeChange.from_dict(item) for item in self.load()["changes"]]

    def update_change(self, change: CodeChange) -> None:
        state = self.load()
        state["changes"] = [change.to_dict() if item["id"] == change.id else item for item in state["changes"]]
        self.save(state)

    def add_run(self, run: EvolutionRun) -> None:
        state = self.load()
        state["runs"].append(run.to_dict())
        self.save(state)

    def runs(self) -> list[EvolutionRun]:
        return [EvolutionRun.from_dict(item) for item in self.load()["runs"]]

    def add_health(self, health: CodebaseHealth) -> None:
        state = self.load()
        state["health"].append(health.to_dict())
        self.save(state)

    def health(self) -> list[CodebaseHealth]:
        return [CodebaseHealth.from_dict(item) for item in self.load()["health"]]

    def add_learning(self, record: dict[str, Any]) -> None:
        state = self.load()
        state["learning"].append(record)
        self.save(state)

    def learning(self) -> list[dict[str, Any]]:
        return self.load()["learning"]

    def _write(self, state: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
