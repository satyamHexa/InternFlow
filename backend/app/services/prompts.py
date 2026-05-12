"""Prompt templates and message builders for all AI operations.

All prompts are versioned constants.  Builder functions return
``list[dict]`` (OpenAI chat messages format) ready for the client.
"""
from __future__ import annotations

# ── Resume parsing ──────────────────────────────────────────────────────────

RESUME_SYSTEM_PROMPT = """\
You are an expert resume parser for a corporate internship programme.
Extract structured information from the supplied resume text.

Respond with VALID JSON ONLY — no markdown fences, no explanation.
Your response MUST conform exactly to this schema:

{
  "name": "<full name or null>",
  "email": "<email address or null>",
  "phone": "<phone number string or null>",
  "summary": "<professional summary or null>",
  "skills": ["<skill>", ...],
  "experience_years": <total years of professional experience as float, or null>,
  "experience_entries": [
    {"title": "<job title>", "company": "<company>", "duration_months": <int or null>}
  ],
  "education": [
    {"degree": "<degree>", "institution": "<institution>", "year": <int or null>}
  ],
  "languages": ["<language>", ...],
  "confidence_score": <float 0.0–1.0>
}

Rules:
- Extract ALL skills: technologies, tools, frameworks, soft skills.
- experience_years = sum of all role durations; estimate if not stated.
- confidence_score: 1.0 = all key fields extracted; 0.0 = nothing useful found.
- Use null for any field you cannot determine — never use empty string for nulls.
"""

_RESUME_USER_TMPL = """\
Resume text:
---
{resume_text}
---
Extract all structured information from this resume."""


def build_resume_messages(resume_text: str) -> list[dict]:
    """Return chat messages for resume extraction."""
    return [
        {"role": "system", "content": RESUME_SYSTEM_PROMPT},
        {"role": "user", "content": _RESUME_USER_TMPL.format(
            resume_text=resume_text[:12_000]  # stay within token budget
        )},
    ]


# ── Email generation ────────────────────────────────────────────────────────

EMAIL_SYSTEM_PROMPT = """\
You are a professional HR communications assistant for an internship
onboarding platform called Intern Flow.

Respond with VALID JSON ONLY — no markdown fences.
Your response MUST conform exactly to this schema:

{
  "subject": "<email subject line>",
  "body": "<full email body in plain text>"
}

Style rules:
- Greet the recipient by first name.
- Keep the body to 2–4 short paragraphs.
- Sign off: "Best regards,\\nThe Intern Flow Team"
- Tone: professional and warm.
"""

# One template string per notification event.  Placeholders use .format() syntax.
EMAIL_BODY_TEMPLATES: dict[str, str] = {
    "referral_submitted": (
        "Write a confirmation email to {recipient_name}. "
        "Their referral has been submitted by {referrer_name} for the "
        "{department} department. HR will review within 2 business days."
    ),
    "nda_pending": (
        "Write an email to {recipient_name} asking them to sign the NDA "
        "document before their internship can proceed. "
        "They must complete this within {deadline_days} business days."
    ),
    "nda_signed": (
        "Write a confirmation email to {recipient_name} thanking them for "
        "signing the NDA. Their mentor {mentor_name} has been assigned. "
        "Next step: complete the joining form."
    ),
    "sla_breach": (
        "Write an internal HR escalation email about an SLA breach. "
        "Task: '{task_name}' for candidate {candidate_name}. "
        "Due: {due_date}. Overdue by {days_overdue} days. "
        "Assigned team: {assigned_team}."
    ),
    "certificate_ready": (
        "Write a congratulatory email to {recipient_name} on completing "
        "their internship. Their certificate is ready in the Intern Flow "
        "portal. Department: {department}. Duration: {duration}."
    ),
    "task_assigned": (
        "Write a task notification email to {recipient_name}. "
        "They have been assigned: '{task_title}'. Due: {due_date}. "
        "They should log in to Intern Flow to complete it."
    ),
    "intern_start_reminder": (
        "Write a reminder email to {recipient_name}. "
        "Their internship start date is {start_date}. "
        "Remind them to complete any pending onboarding tasks."
    ),
}

_EMAIL_USER_TMPL = "Write an email for this context:\n{context_text}"


def build_email_messages(event: str, context: dict) -> list[dict]:
    """Return chat messages for email generation.

    Falls back to a generic template when the event is unknown.
    """
    template = EMAIL_BODY_TEMPLATES.get(event)
    if template:
        try:
            context_text = template.format(**context)
        except KeyError:
            # Missing placeholder — still render what we can
            context_text = template
    else:
        context_text = (
            f"Event: {event}\n"
            f"Recipient: {context.get('recipient_name', 'the candidate')}\n"
            f"Additional details: {context}"
        )

    return [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": _EMAIL_USER_TMPL.format(context_text=context_text)},
    ]


# ── Duplicate detection ─────────────────────────────────────────────────────

DUPLICATE_SYSTEM_PROMPT = """\
You are a duplicate-candidate detection assistant for an internship referral system.

Given a new candidate and a list of existing referral records, determine whether
the new candidate is already in the system.

Respond with VALID JSON ONLY — no markdown fences.
Your response MUST conform exactly to this schema:

{
  "is_duplicate": <true or false>,
  "confidence": <float 0.0–1.0>,
  "matched_email": "<email of the matched record, or null>",
  "reason": "<one sentence explanation>"
}

Rules:
- Exact email match → is_duplicate=true, confidence=1.0 (highest priority signal).
- Name variations count (Nick/Nicholas, hyphenated surnames, Jr./Junior).
- If confidence < 0.70 → is_duplicate=false.
- Respond with JSON ONLY.
"""

_DUPLICATE_USER_TMPL = """\
New candidate:
  Name:  {candidate_name}
  Email: {candidate_email}

Existing referrals ({count} records):
{existing_list}

Is the new candidate a duplicate of any existing referral?"""


def build_duplicate_messages(
    candidate_name: str,
    candidate_email: str,
    existing: list[dict],
) -> list[dict]:
    """Return chat messages for duplicate detection.

    ``existing`` items must have at minimum ``email`` and ``name`` keys.
    We truncate to 80 records to stay within token budget.
    """
    records = existing[:80]
    lines = "\n".join(
        f"  {i + 1}. Name: {r.get('candidate_name', '?')} | Email: {r.get('candidate_email', '?')}"
        for i, r in enumerate(records)
    )
    return [
        {"role": "system", "content": DUPLICATE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _DUPLICATE_USER_TMPL.format(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                count=len(records),
                existing_list=lines or "  (none)",
            ),
        },
    ]
