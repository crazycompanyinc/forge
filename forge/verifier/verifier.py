from __future__ import annotations

from pathlib import Path

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.executor.test_runner import TestRunner
from forge.verifier.safety import SafetyChecker


class ChangeVerifier:
    def __init__(self) -> None:
        self.safety = SafetyChecker()
        self.tests = TestRunner()
        self.analyzer = CodebaseAnalyzer()

    def verify(self, path: str | Path = ".") -> dict[str, object]:
        syntax_ok, safety_errors = self.safety.check(path)
        tests_ok, test_output = self.tests.run(path)
        health = self.analyzer.analyze(path)
        return {
            "syntax_ok": syntax_ok,
            "tests_ok": tests_ok,
            "safety_errors": safety_errors,
            "test_output": test_output,
            "health": health.to_dict(),
            "verified": syntax_ok and tests_ok,
        }
