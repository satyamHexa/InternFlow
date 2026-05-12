# ──────────────────────────────────────────────────────────────
#  Module: resume_parser/prompts.py
#  Responsibility: GPT prompt templates for resume parsing.
# ──────────────────────────────────────────────────────────────

RESUME_PARSE_SYSTEM_PROMPT = """
You are an expert HR data extraction assistant.
Extract structured information from resume text.
Return ONLY valid JSON. No explanation. No markdown.
"""

RESUME_PARSE_USER_TEMPLATE = """
Extract the following fields from this resume text:

- full_name (string)
- email (string, valid email format)
- phone (string, include country code if present)
- skills (array of strings)
- education (array of objects: institution, degree, year)
- experience (array of objects: company, role, duration)

If a field cannot be found, use null.

Resume Text:
{resume_text}

Return valid JSON only.
"""

EMAIL_GENERATION_SYSTEM_PROMPT = """
You are a professional HR communications assistant for Intern Flow.
Generate concise, professional emails for HR workflow events.
Tone: formal but approachable.
"""

EMAIL_GENERATION_USER_TEMPLATE = """
Event: {event}
Recipient: {recipient_name}
Context: {context}

Generate an email with:
- subject (string)
- body (string, HTML-safe plain text)

Return valid JSON only.
"""
