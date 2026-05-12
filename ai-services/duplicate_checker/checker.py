# ──────────────────────────────────────────────────────────────
#  Module: duplicate_checker/checker.py
#  Responsibility: Detect duplicate intern referrals.
#
#  Class: DuplicateChecker
#    Methods:
#      check(candidate_email, candidate_name, db_client) → DuplicateResult
#        - Step 1: Exact email match in referrals table
#          If found → is_duplicate=True, confidence=1.0
#        - Step 2: Fuzzy name match (Levenshtein distance ≤ 2)
#          within same department
#          If found → is_duplicate=True, confidence=0.7
#        - Returns: DuplicateResult(is_duplicate, confidence,
#                                   duplicate_referral_id)
# ──────────────────────────────────────────────────────────────
# TODO: Implement
