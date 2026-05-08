from __future__ import annotations

from forge.verifier.rollback import RollbackManager
from forge.verifier.safety import SafetyChecker
from forge.verifier.verifier import ChangeVerifier


def test_safety_checker_accepts_demo(demo_root) -> None:
    ok, errors = SafetyChecker().check(demo_root)
    assert ok
    assert errors == []


def test_safety_checker_finds_syntax_error(tmp_path) -> None:
    (tmp_path / "bad.py").write_text("def nope(:\n", encoding="utf-8")
    ok, errors = SafetyChecker().check(tmp_path)
    assert not ok
    assert errors


def test_rollback_restores_file(demo_root) -> None:
    manager = RollbackManager()
    snapshot = manager.snapshot(demo_root)
    path = demo_root / "requirements.txt"
    path.write_text("broken", encoding="utf-8")
    manager.restore(demo_root, snapshot)
    assert path.read_text(encoding="utf-8") == "requests==2.25\n"


def test_verifier_returns_health(demo_root) -> None:
    result = ChangeVerifier().verify(demo_root)
    assert result["verified"] is True
    assert "health" in result
