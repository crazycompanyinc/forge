from __future__ import annotations

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.analysis.metrics import MetricsCollector
from forge.analysis.scanner import HealthScanner


def test_scanner_finds_security_issue(demo_root) -> None:
    issues = HealthScanner().scan(demo_root)
    assert any(issue["type"] == "security" for issue in issues)


def test_scanner_finds_dependency_issue(demo_root) -> None:
    issues = HealthScanner().scan(demo_root)
    assert any(issue["type"] == "dependency" for issue in issues)


def test_scanner_finds_performance_issue(demo_root) -> None:
    issues = HealthScanner().scan(demo_root)
    assert any(issue["type"] == "performance" for issue in issues)


def test_metrics_collect_counts_files(demo_root) -> None:
    issues = HealthScanner().scan(demo_root)
    metrics = MetricsCollector().collect(demo_root, issues)
    assert metrics["python_files"] >= 3


def test_analyzer_scores_health(demo_root) -> None:
    health = CodebaseAnalyzer().analyze(demo_root)
    assert 0 <= health.overall_score <= 100
    assert health.categories["security"] < 100


def test_analyzer_reports_debt_items(demo_root) -> None:
    health = CodebaseAnalyzer().analyze(demo_root)
    assert len(health.debt_items) >= 8
