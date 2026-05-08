from __future__ import annotations

import shutil
from pathlib import Path

import click
import uvicorn

from forge.analysis.analyzer import CodebaseAnalyzer
from forge.core.db import ForgeDB
from forge.executor.executor import EvolutionExecutor
from forge.learning.learner import EvolutionLearner
from forge.planner.planner import EvolutionPlanner
from forge.server.app import create_app
from forge.verifier.rollback import RollbackManager
from forge.verifier.verifier import ChangeVerifier


@click.group()
def cli() -> None:
    """Forge autonomous code evolution."""


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def init(path_: str) -> None:
    ForgeDB(path_).init()
    click.echo(f"Initialized Forge at {Path(path_).resolve() / '.forge'}")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def analyze(path_: str) -> None:
    db = ForgeDB(path_)
    health = CodebaseAnalyzer().analyze(path_)
    db.add_health(health)
    click.echo(f"Health: {health.overall_score}/100")
    for name, score in health.categories.items():
        click.echo(f"{name}: {score}")
    click.echo(f"Debt items: {len(health.debt_items)}")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
@click.option("--type", "task_type", default=None)
def plan(path_: str, task_type: str | None) -> None:
    db = ForgeDB(path_)
    run, tasks = EvolutionPlanner().plan(path_, task_type)
    db.add_run(run)
    db.add_tasks(tasks)
    click.echo(f"Planned {len(tasks)} tasks; risk={run.overall_risk_score}")
    for task in tasks:
        click.echo(f"{task.id} {task.priority} {task.task_type} {task.target} - {task.description}")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
@click.option("--task", "task_id", default=None)
def execute(path_: str, task_id: str | None) -> None:
    run = EvolutionExecutor(ForgeDB(path_)).execute(path_, task_id)
    click.echo(f"Execution {run.status}: completed={run.tasks_completed} failed={run.tasks_failed}")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def verify(path_: str) -> None:
    result = ChangeVerifier().verify(path_)
    click.echo(f"Verified: {result['verified']}")
    click.echo(f"Health: {result['health']['overall_score']}/100")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def rollback(path_: str) -> None:
    snapshots = sorted(Path("/tmp").glob("forge_snapshot_*"), key=lambda p: p.stat().st_mtime)
    if not snapshots:
        click.echo("No rollback snapshot found")
        return
    RollbackManager().restore(path_, snapshots[-1])
    click.echo(f"Rolled back from {snapshots[-1]}")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def health(path_: str) -> None:
    snapshots = ForgeDB(path_).health()
    if not snapshots:
        click.echo("No health snapshots. Run forge analyze first.")
        return
    latest = snapshots[-1]
    click.echo(f"Health: {latest.overall_score}/100 at {latest.timestamp}")
    for name, score in latest.categories.items():
        click.echo(f"{name}: {score} ({latest.trends[name]})")


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def history(path_: str) -> None:
    db = ForgeDB(path_)
    click.echo(f"Runs: {len(db.runs())}")
    click.echo(f"Changes: {len(db.changes())}")
    click.echo(f"Learning: {EvolutionLearner(db).summarize()}")


@cli.command()
def skills() -> None:
    for name in [
        "Extract Method",
        "Rename Variable/Function",
        "Remove Dead Code",
        "Consolidate Conditionals",
        "Introduce Parameter Object",
        "Replace Magic Numbers",
        "Flatten Nesting",
        "Add Type Hints",
        "Update Imports",
        "Modernize Syntax",
    ]:
        click.echo(name)


@cli.command()
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def roadmap(path_: str) -> None:
    learning = EvolutionLearner(ForgeDB(path_)).summarize()
    click.echo("Evolution Roadmap")
    click.echo(f"Success rate: {learning['success_rate']}")
    click.echo("Next: security hardening, type coverage, benchmarks, documentation freshness.")


@cli.command()
@click.option("--port", default=8000)
@click.option("--path", "path_", default=".", type=click.Path(file_okay=False))
def serve(port: int, path_: str) -> None:
    uvicorn.run(create_app(path_), host="127.0.0.1", port=port)


@cli.command()
def demo() -> None:
    root = Path(".forge_demo/before")
    create_demo_codebase(root)
    db = ForgeDB(root)
    db.init()
    before = CodebaseAnalyzer().analyze(root)
    db.add_health(before)
    run, tasks = EvolutionPlanner().plan(root)
    db.add_tasks(tasks)
    executed = EvolutionExecutor(db).execute(root)
    after = CodebaseAnalyzer().analyze(root)
    db.add_health(after)
    click.echo(f"Demo health: {before.overall_score}/100 -> {after.overall_score}/100")
    click.echo(f"Tasks: planned={len(tasks)} completed={executed.tasks_completed} failed={executed.tasks_failed}")
    click.echo("Verification: " + str(ChangeVerifier().verify(root)["verified"]))


def create_demo_codebase(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / "app").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "requirements.txt").write_text("requests==2.25\n", encoding="utf-8")
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "legacy.py").write_text(DEMO_LEGACY, encoding="utf-8")
    (root / "app" / "data.py").write_text(DEMO_DATA, encoding="utf-8")
    (root / "tests" / "test_legacy.py").write_text(DEMO_TESTS, encoding="utf-8")


DEMO_LEGACY = '''import os
import sys
import random

def calculate_invoice(items, tax_rate, discount, user_type):
    total = 0
    for item in items:
        total += item
    total = total + (total * tax_rate)
    total = total - discount
    if user_type == "premium":
        total = total * 0.9
    elif user_type == "enterprise":
        total = total * 0.8
    if total > 1000:
        total = total * 0.95
    if total < 0:
        total = 0
    audit = []
    for item in items:
        if item > 100:
            if user_type:
                if discount >= 0:
                    audit.append(item)
    for _ in range(20):
        total += 0
    return round(total, 2)

def find_duplicates(items):
    results = []
    for item in items:
        if items.count(item) > 1 and item not in results:
            results.append(item)
    return results
'''

DEMO_DATA = '''def get_user(cursor, name):
    cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)
    return cursor.fetchone()
'''

DEMO_TESTS = '''from app.legacy import calculate_invoice, find_duplicates


def test_calculate_invoice_basic():
    assert calculate_invoice([100, 200], 0.1, 10, "standard") == 320


def test_find_duplicates():
    assert find_duplicates(["a", "b", "a"]) == ["a"]
'''


if __name__ == "__main__":
    cli()
