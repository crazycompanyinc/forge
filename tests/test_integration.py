from __future__ import annotations

from click.testing import CliRunner

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.cli import cli
from forge.core.db import ForgeDB
from forge.executor.executor import EvolutionExecutor
from forge.learning.learner import EvolutionLearner
from forge.planner.planner import EvolutionPlanner
from forge.server.app import create_app


def test_full_cycle_improves_health(demo_root) -> None:
    db = ForgeDB(demo_root)
    before = CodebaseAnalyzer().analyze(demo_root)
    _, tasks = EvolutionPlanner().plan(demo_root)
    db.add_tasks(tasks)
    run = EvolutionExecutor(db).execute(demo_root)
    after = CodebaseAnalyzer().analyze(demo_root)
    assert run.tasks_completed > 0
    assert after.overall_score >= before.overall_score


def test_learning_summary(demo_root) -> None:
    db = ForgeDB(demo_root)
    db.add_tasks(EvolutionPlanner().plan(demo_root, "security")[1])
    EvolutionExecutor(db).execute(demo_root)
    summary = EvolutionLearner(db).summarize()
    assert summary["total_attempts"] >= 1


def test_cli_init_analyze_plan(demo_root) -> None:
    runner = CliRunner()
    assert runner.invoke(cli, ["init", "--path", str(demo_root)]).exit_code == 0
    assert runner.invoke(cli, ["analyze", "--path", str(demo_root)]).exit_code == 0
    result = runner.invoke(cli, ["plan", "--path", str(demo_root)])
    assert result.exit_code == 0
    assert "Planned" in result.output


def test_cli_skills_lists_builtins() -> None:
    result = CliRunner().invoke(cli, ["skills"])
    assert result.exit_code == 0
    assert "Extract Method" in result.output


def test_cli_demo_runs() -> None:
    result = CliRunner().invoke(cli, ["demo"])
    assert result.exit_code == 0
    assert "Demo health" in result.output


def test_server_app_routes_exist() -> None:
    app = create_app(".")
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/plan" in paths
    assert "/execute" in paths
