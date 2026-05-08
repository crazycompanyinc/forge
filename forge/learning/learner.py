from __future__ import annotations

from forge.core.db import ForgeDB
from forge.learning.patterns import PatternMiner


class EvolutionLearner:
    def __init__(self, db: ForgeDB | None = None) -> None:
        self.db = db or ForgeDB()
        self.patterns = PatternMiner()

    def summarize(self) -> dict[str, object]:
        records = self.db.learning()
        mined = self.patterns.mine(records)
        total = len(records)
        successes = sum(1 for record in records if record.get("success"))
        return {"total_attempts": total, "success_rate": round(successes / max(total, 1), 2), **mined}
