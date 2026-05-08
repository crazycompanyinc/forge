from __future__ import annotations

from forge.core.db import ForgeDB
from forge.core.models import EvolutionTask, utc_now


class SuccessTracker:
    def __init__(self, db: ForgeDB) -> None:
        self.db = db

    def record(self, task: EvolutionTask, success: bool, message: str) -> None:
        self.db.add_learning({"task_id": task.id, "task_type": task.task_type, "success": success, "message": message, "timestamp": utc_now()})
