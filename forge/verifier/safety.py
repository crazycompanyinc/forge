from __future__ import annotations

import ast
from pathlib import Path


class SafetyChecker:
    def check(self, path: str | Path = ".") -> tuple[bool, list[str]]:
        errors: list[str] = []
        for file_path in Path(path).rglob("*.py"):
            if any(part in {".forge", ".venv", "__pycache__"} for part in file_path.parts):
                continue
            try:
                ast.parse(file_path.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                errors.append(f"{file_path}: {exc}")
        return not errors, errors
