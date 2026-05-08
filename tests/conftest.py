from __future__ import annotations

from pathlib import Path

import pytest

from forge.cli import create_demo_codebase


@pytest.fixture()
def demo_root(tmp_path: Path) -> Path:
    root = tmp_path / "demo"
    create_demo_codebase(root)
    return root
