from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


class TestRunner:
    def run(self, path: str | Path = ".") -> tuple[bool, str]:
        root = Path(path)
        tests = root / "tests"
        if not tests.exists():
            return True, "No tests found; treated as pass for low-risk local evolution."
        env = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--rootdir=.", "tests", "-q"],
            cwd=root,
            text=True,
            capture_output=True,
            timeout=60,
            env=env,
        )
        return result.returncode == 0, result.stdout + result.stderr
