from __future__ import annotations

from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    total_referrals: int
    pending_ndas: int
    active_interns: int
    sla_breaches: int
    delayed_onboarding: int
    completed_this_month: int


class SLAReport(BaseModel):
    task_name: str
    total: int
    on_track: int
    at_risk: int
    breached: int


class DepartmentData(BaseModel):
    department: str
    count: int


class WeeklyTrend(BaseModel):
    week: str
    submitted: int
    completed: int
    breached: int


class StatusFunnelItem(BaseModel):
    stage: str
    count: int
