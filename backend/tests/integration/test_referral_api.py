# ──────────────────────────────────────────────────────────────
#  Tests: tests/integration/test_referral_api.py
#  Tests:
#    - POST /referrals/create → 201
#    - POST /referrals/create with duplicate → 409 (or duplicate flag)
#    - GET  /referrals/{id} → 200 with correct shape
#    - GET  /referrals as employee role → 403 (can't list all)
#    - PUT  /referrals/{id} as hr → 200
# ──────────────────────────────────────────────────────────────
# TODO: Implement
