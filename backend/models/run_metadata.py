"""
models/run_metadata.py — Pydantic v2 models for validation run records.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ViolationCounts(BaseModel):
    schedule_issues: int = 0
    bh_violations: int = 0
    dh_violations: int = 0
    sector_violations: int = 0
    pairing_issues: int = 0
    status_issues: int = 0
    overnight_issues: int = 0
    aircraft_issues: int = 0


class RunMetadata(BaseModel):
    run_id: str
    date: str
    vendor: str
    timestamp: str
    triggered_by: str
    status: Literal["complete", "failed"]
    violation_counts: ViolationCounts
    total_violations: int = Field(default=0)
    available_crew: int = Field(default=0)
    scheduled_crew: int = Field(default=0)


class RunSummary(BaseModel):
    """Lightweight record stored in index.json for fast listing."""
    run_id: str
    date: str
    vendor: str
    timestamp: str
    status: Literal["complete", "failed"]
    total_violations: int = Field(default=0)
