from __future__ import annotations

from collections import Counter


class PatternMiner:
    def mine(self, records: list[dict[str, object]]) -> dict[str, object]:
        counts = Counter(str(record["task_type"]) for record in records)
        success = Counter(str(record["task_type"]) for record in records if record.get("success"))
        return {"attempts_by_type": dict(counts), "successes_by_type": dict(success)}
