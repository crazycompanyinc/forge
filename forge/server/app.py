from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.core.db import ForgeDB
from forge.executor.executor import EvolutionExecutor
from forge.planner.planner import EvolutionPlanner
from forge.verifier.verifier import ChangeVerifier


def create_app(root: str | Path = ".") -> FastAPI:
    app = FastAPI(title="Forge", version="0.1.0")
    db = ForgeDB(root)

    @app.get("/health")
    def health() -> dict[str, object]:
        result = CodebaseAnalyzer().analyze(root)
        db.add_health(result)
        return result.to_dict()

    @app.post("/plan")
    def plan(task_type: str | None = None) -> dict[str, object]:
        run, tasks = EvolutionPlanner().plan(root, task_type)
        db.add_run(run)
        db.add_tasks(tasks)
        return {"run": run.to_dict(), "tasks": [task.to_dict() for task in tasks]}

    @app.post("/execute")
    def execute(task_id: str | None = None) -> dict[str, object]:
        return EvolutionExecutor(db).execute(root, task_id).to_dict()

    @app.get("/verify")
    def verify() -> dict[str, object]:
        return ChangeVerifier().verify(root)

    @app.post("/webhook")
    def webhook(payload: dict[str, object]) -> dict[str, object]:
        return {"accepted": True, "event": payload.get("event", "unknown")}

    return app
