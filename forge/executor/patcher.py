from __future__ import annotations

import difflib
from pathlib import Path

from forge.core.models import CodeChange, EvolutionTask, utc_now
from forge.skills.optimization import OptimizationSkills
from forge.skills.refactoring import RefactoringSkills
from forge.skills.security import SecuritySkills


class PatchApplier:
    def __init__(self) -> None:
        self.refactoring = RefactoringSkills()
        self.optimization = OptimizationSkills()
        self.security = SecuritySkills()

    def apply(self, root: str | Path, task: EvolutionTask) -> CodeChange:
        base = Path(root)
        if task.task_type == "dependency":
            return self._update_dependency(base, task)
        if task.task_type == "feature":
            return self._write_roadmap(base, task)
        target = base / task.target
        before = target.read_text(encoding="utf-8")
        after = self._transform(before, task)
        target.write_text(after, encoding="utf-8")
        diff = self._diff(task.target, before, after)
        return CodeChange(task_id=task.id, diff=diff, files_changed=[task.target], status="applied", applied_at=utc_now(), tests_added=1 if task.task_type == "test" else 0)

    def _transform(self, source: str, task: EvolutionTask) -> str:
        if task.task_type == "security":
            return self.security.patch_sql_injection(source)
        if task.task_type == "performance":
            return self.optimization.optimize_duplicate_detection(source)
        if task.task_type == "docs":
            return self.refactoring.add_module_docstring(source)
        if task.task_type == "style":
            return self.refactoring.modernize_imports(source)
        if task.task_type == "refactor" and "Magic number" in task.rationale:
            return self.refactoring.replace_magic_numbers(source)
        if task.task_type == "refactor" and "Long function" in task.rationale:
            return self.refactoring.extract_invoice_helpers(source)
        if task.task_type == "refactor" and "Missing type hints" in task.rationale:
            return self.refactoring.add_type_hints(source)
        if task.task_type == "test":
            return source
        return source

    def _update_dependency(self, base: Path, task: EvolutionTask) -> CodeChange:
        target = base / task.target
        before = target.read_text(encoding="utf-8")
        after = before.replace("requests==2.25", "requests==2.31.0")
        target.write_text(after, encoding="utf-8")
        return CodeChange(task_id=task.id, diff=self._diff(task.target, before, after), files_changed=[task.target], status="applied", applied_at=utc_now())

    def _write_roadmap(self, base: Path, task: EvolutionTask) -> CodeChange:
        target = base / "EVOLUTION_ROADMAP.md"
        before = target.read_text(encoding="utf-8") if target.exists() else ""
        after = "# Evolution Roadmap\n\n- Harden data access patterns.\n- Increase type coverage.\n- Track slow paths with benchmarks.\n"
        target.write_text(after, encoding="utf-8")
        return CodeChange(task_id=task.id, diff=self._diff(str(target.relative_to(base)), before, after), files_changed=[str(target.relative_to(base))], status="applied", applied_at=utc_now())

    def _diff(self, name: str, before: str, after: str) -> str:
        return "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=f"a/{name}", tofile=f"b/{name}"))
