from __future__ import annotations

import shutil
import tempfile
from pathlib import Path


class RollbackManager:
    def snapshot(self, path: str | Path) -> Path:
        root = Path(path)
        dest = Path(tempfile.mkdtemp(prefix="forge_snapshot_"))
        for item in root.iterdir():
            if item.name in {".forge", ".git", "__pycache__"}:
                continue
            target = dest / item.name
            if item.is_dir():
                shutil.copytree(item, target, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
            else:
                shutil.copy2(item, target)
        return dest

    def restore(self, path: str | Path, snapshot: str | Path) -> None:
        root = Path(path)
        keep = {".forge", ".git"}
        for item in root.iterdir():
            if item.name in keep:
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        for item in Path(snapshot).iterdir():
            target = root / item.name
            if item.is_dir():
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
