from __future__ import annotations

import subprocess
import sys
from pathlib import Path


class TestRunner:
    def run(self, path: str | Path = ".") -> tuple[bool, str]:
        root = Path(path)
        tests = root / "tests"
        if not tests.exists():
            return True, "No tests found; treated as pass for low-risk local evolution."
        result = subprocess.run([sys.executable, "-m", "pytest", str(tests)], cwd=root, text=True, capture_output=True, timeout=60)
        return result.returncode == 0, result.stdout + result.stderr
