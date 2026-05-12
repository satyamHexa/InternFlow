# ──────────────────────────────────────────────────────────────
#  Module: resume_parser/confidence.py
#  Responsibility: Calculate a parse confidence score (0.0–1.0).
#
#  Algorithm:
#    - Start at 1.0
#    - Deduct 0.15 for each required field that is null
#      (full_name, email, phone, skills, education, experience)
#    - Deduct 0.05 if email format is invalid
#    - Deduct 0.10 if skills array is empty
#    - Cap at 0.0 minimum
#
#  Returns: float  (e.g. 0.85)
# ──────────────────────────────────────────────────────────────
# TODO: Implement
