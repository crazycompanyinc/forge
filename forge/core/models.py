from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

TaskType = Literal["refactor", "dependency", "security", "performance", "test", "docs", "style", "feature"]
Priority = Literal["critical", "high", "medium", "low"]
Risk = Literal["safe", "moderate", "risky"]
TaskStatus = Literal["planned", "approved", "executing", "verifying", "completed", "failed", "rolled_back"]
ChangeStatus = Literal["pending", "applied", "verified", "rolled_back"]
RunStatus = Literal["running", "completed", "failed", "rolled_back"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class EvolutionTask:
    task_type: TaskType
    target: str
    description: str
    rationale: str
    priority: Priority = "medium"
    estimated_risk: Risk = "safe"
    status: TaskStatus = "planned"
    id: str = field(default_factory=lambda: new_id("task"))
    created_at: str = field(default_factory=utc_now)
    completed_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvolutionTask":
        return cls(**data)


@dataclass
class CodeChange:
    task_id: str
    diff: str
    files_changed: list[str]
    tests_added: int = 0
    tests_passed: bool = False
    status: ChangeStatus = "pending"
    id: str = field(default_factory=lambda: new_id("change"))
    applied_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeChange":
        return cls(**data)


@dataclass
class EvolutionRun:
    tasks_planned: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    overall_risk_score: float = 0.0
    status: RunStatus = "running"
    id: str = field(default_factory=lambda: new_id("run"))
    started_at: str = field(default_factory=utc_now)
    completed_at: str | None = None
    task_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvolutionRun":
        return cls(**data)


@dataclass
class CodebaseHealth:
    overall_score: int
    categories: dict[str, int]
    debt_items: list[dict[str, Any]]
    trends: dict[str, str]
    snapshot_id: str = field(default_factory=lambda: new_id("health"))
    timestamp: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodebaseHealth":
        return cls(**data)
