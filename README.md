# Forge

Forge is a local autonomous code evolution system. It analyzes a Python codebase, plans targeted improvements, applies safe deterministic changes, verifies them with tests and safety checks, and records outcomes for future planning.

## Capabilities

- Continuous codebase health analysis
- Refactoring, dependency, security, performance, test, docs, style, and feature planning
- One-change-at-a-time execution with rollback snapshots
- Verification through test runs, safety checks, and health comparison
- Learning records for successful and failed changes
- Click CLI and FastAPI server
- Built-in demo codebase with intentional issues

## Quick Start

```bash
pip install -e ".[dev]"
forge init
forge demo
forge analyze --path .forge_demo/before
forge plan --path .forge_demo/before
forge execute --path .forge_demo/before
forge verify --path .forge_demo/before
forge health
```

## CLI

```bash
forge init
forge analyze [--path PATH]
forge plan [--path PATH] [--type TYPE]
forge execute [--path PATH] [--task TASK_ID]
forge verify [--path PATH]
forge rollback [--path PATH]
forge health
forge history
forge skills
forge roadmap
forge serve --port 8000
forge demo
```

Forge is intentionally conservative: built-in skills operate on recognizable demo and common Python patterns, then verification decides whether changes stay applied.
