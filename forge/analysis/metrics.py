from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


class MetricsCollector:
    def collect(self, path: str | Path, issues: list[dict[str, Any]]) -> dict[str, Any]:
        root = Path(path)
        py_files = [p for p in root.rglob("*.py") if ".forge" not in p.parts and "__pycache__" not in p.parts]
        test_files = [p for p in py_files if p.name.startswith("test_") or "tests" in p.parts]
        counts = Counter(issue["type"] for issue in issues)
        loc = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in py_files)
        return {
            "python_files": len(py_files),
            "test_files": len(test_files),
            "lines_of_code": loc,
            "issue_counts": dict(counts),
            "test_ratio": round(len(test_files) / max(len(py_files), 1), 2),
        }
