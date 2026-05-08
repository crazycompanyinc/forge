from __future__ import annotations

from forge.core.models import EvolutionTask


class TaskGenerator:
    def generate(self, debt_items: list[dict[str, str]], task_type: str | None = None) -> list[EvolutionTask]:
        tasks: list[EvolutionTask] = []
        seen: set[tuple[str, str, str]] = set()
        for issue in debt_items:
            kind = issue["type"]
            if task_type and kind != task_type:
                continue
            key = (kind, issue["target"], issue["description"])
            if key in seen:
                continue
            seen.add(key)
            tasks.append(
                EvolutionTask(
                    task_type=kind,  # type: ignore[arg-type]
                    target=issue["target"],
                    description=self._task_description(issue),
                    rationale=issue["description"],
                    priority=self._priority(issue["severity"]),
                    estimated_risk=self._risk(kind, issue["severity"]),
                    metadata={"symbol": issue.get("symbol")},
                )
            )
        if not task_type or task_type == "feature":
            tasks.append(
                EvolutionTask(
                    task_type="feature",
                    target="roadmap",
                    description="Suggest feature roadmap from recurring debt patterns",
                    rationale="Feature suggestions help turn repeated maintenance issues into product direction.",
                    priority="low",
                    estimated_risk="safe",
                )
            )
        return tasks

    def _task_description(self, issue: dict[str, str]) -> str:
        return {
            "security": "Patch security vulnerability",
            "dependency": "Update outdated dependency",
            "performance": "Optimize performance anti-pattern",
            "refactor": "Apply safe refactoring",
            "style": "Clean code style issue",
            "docs": "Synchronize documentation with code",
            "test": "Improve test coverage",
        }.get(issue["type"], "Evolve codebase")

    def _priority(self, severity: str) -> str:
        return {"critical": "critical", "high": "high", "medium": "medium"}.get(severity, "low")

    def _risk(self, kind: str, severity: str) -> str:
        if kind in {"security", "dependency"}:
            return "moderate"
        return "safe" if severity in {"low", "medium"} else "moderate"
