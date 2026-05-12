from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ── Sub-models ─────────────────────────────────────────────────────────────

class EducationEntry(BaseModel):
    degree: str | None = None
    institution: str | None = None
    year: int | None = None


class ExperienceEntry(BaseModel):
    title: str | None = None
    company: str | None = None
    duration_months: int | None = None


# ── Primary output models ───────────────────────────────────────────────────

class ParsedResume(BaseModel):
    """Structured resume data extracted by the AI pipeline."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    experience_entries: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    confidence_score: float = 0.0

    @field_validator("confidence_score")
    @classmethod
    def clamp_score(cls, v: float) -> float:
        return round(max(0.0, min(1.0, v)), 4)

    @field_validator("skills", "languages", mode="before")
    @classmethod
    def deduplicate_list(cls, v: list) -> list:
        seen: set = set()
        result = []
        for item in v:
            if isinstance(item, str):
                item = item.strip()
            key = str(item).lower() if item else ""
            if key and key not in seen:
                seen.add(key)
                result.append(item)
        return result


class EmailContent(BaseModel):
    """Generated email subject and body."""

    subject: str
    body: str
    recipient_name: str | None = None


class DuplicateResult(BaseModel):
    """Outcome of duplicate-candidate detection."""

    is_duplicate: bool
    confidence: float
    matched_email: str | None = None
    matched_referral_id: str | None = None
    reason: str | None = None

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return round(max(0.0, min(1.0, v)), 4)
