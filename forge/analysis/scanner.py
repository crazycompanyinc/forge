from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


class HealthScanner:
    def scan(self, path: str | Path) -> list[dict[str, Any]]:
        root = Path(path)
        issues: list[dict[str, Any]] = []
        for file_path in sorted(root.rglob("*.py")):
            if any(part in {".forge", ".venv", "__pycache__"} for part in file_path.parts):
                continue
            source = file_path.read_text(encoding="utf-8")
            rel = str(file_path.relative_to(root))
            issues.extend(self._scan_source(rel, source))
        req = root / "requirements.txt"
        if req.exists() and "requests==2.25" in req.read_text(encoding="utf-8"):
            issues.append(self._issue("dependency", "requirements.txt", "Outdated requests dependency", "high"))
        return issues

    def _scan_source(self, rel: str, source: str) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return [self._issue("style", rel, f"Syntax error: {exc.msg}", "critical")]

        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) and node.names]
        used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        for name in imports:
            base = name.split(".")[0]
            if base not in used_names and base not in {"typing"}:
                issues.append(self._issue("style", rel, f"Unused import: {base}", "low"))

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                length = max([getattr(child, "end_lineno", node.lineno) for child in ast.walk(node)], default=node.lineno) - node.lineno + 1
                if length >= 40:
                    issues.append(self._issue("refactor", rel, f"Long function {node.name} spans {length} lines", "medium", node.name))
                if not node.returns or any(arg.annotation is None for arg in node.args.args):
                    issues.append(self._issue("refactor", rel, f"Missing type hints in {node.name}", "medium", node.name))
                nested = self._max_if_depth(node)
                if nested >= 3:
                    issues.append(self._issue("refactor", rel, f"Deep nesting in {node.name}", "medium", node.name))

            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and node.value not in {0, 1, -1}:
                issues.append(self._issue("refactor", rel, f"Magic number: {node.value}", "low"))

            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod) and self._contains_execute_context(tree, node):
                issues.append(self._issue("security", rel, "Possible SQL injection via string formatting", "critical"))

        if "for " in source and ".append(" in source and " in results" in source:
            issues.append(self._issue("performance", rel, "Possible O(n^2) duplicate detection loop", "high"))
        if '"""' not in source and "'''" not in source:
            issues.append(self._issue("docs", rel, "Missing module documentation", "low"))
        return issues

    def _contains_execute_context(self, tree: ast.AST, target: ast.AST) -> bool:
        for call in ast.walk(tree):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr == "execute":
                if any(child is target for child in ast.walk(call)):
                    return True
        return False

    def _max_if_depth(self, node: ast.AST, depth: int = 0) -> int:
        if isinstance(node, ast.If):
            depth += 1
        children = list(ast.iter_child_nodes(node))
        return max([depth, *[self._max_if_depth(child, depth) for child in children]])

    def _issue(self, kind: str, target: str, description: str, severity: str, symbol: str | None = None) -> dict[str, Any]:
        return {"type": kind, "target": target, "description": description, "severity": severity, "symbol": symbol}
