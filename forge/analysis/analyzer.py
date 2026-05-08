from __future__ import annotations

from pathlib import Path

from forge.analysis.metrics import MetricsCollector
from forge.analysis.scanner import HealthScanner
from forge.core.models import CodebaseHealth


class CodebaseAnalyzer:
    def __init__(self) -> None:
        self.scanner = HealthScanner()
        self.metrics = MetricsCollector()

    def analyze(self, path: str | Path = ".") -> CodebaseHealth:
        issues = self.scanner.scan(path)
        metrics = self.metrics.collect(path, issues)
        categories = self._score_categories(issues, metrics)
        overall = round(sum(categories.values()) / len(categories))
        return CodebaseHealth(overall_score=overall, categories=categories, debt_items=issues, trends=self._trends(categories))

    def _score_categories(self, issues: list[dict[str, str]], metrics: dict[str, object]) -> dict[str, int]:
        penalties = {"security": 0, "performance": 0, "maintainability": 0, "test_coverage": 0, "documentation": 0}
        for issue in issues:
            weight = {"critical": 35, "high": 20, "medium": 10, "low": 5}.get(issue["severity"], 5)
            kind = issue["type"]
            if kind == "security":
                penalties["security"] += weight
            elif kind == "performance":
                penalties["performance"] += weight
            elif kind in {"refactor", "style"}:
                penalties["maintainability"] += weight
            elif kind == "test":
                penalties["test_coverage"] += weight
            elif kind == "docs":
                penalties["documentation"] += weight
            elif kind == "dependency":
                penalties["security"] += 8
                penalties["maintainability"] += 5
        test_ratio = float(metrics["test_ratio"])
        penalties["test_coverage"] += max(0, int((0.5 - test_ratio) * 70))
        return {name: max(0, 100 - penalty) for name, penalty in penalties.items()}

    def _trends(self, categories: dict[str, int]) -> dict[str, str]:
        return {name: "improving" if score >= 80 else "worsening" for name, score in categories.items()}
