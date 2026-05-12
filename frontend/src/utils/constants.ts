// ──────────────────────────────────────────────────────────────
//  Module: src/utils/constants.ts
//  Responsibility: Application-wide constants.
// ──────────────────────────────────────────────────────────────

export const WORKFLOW_STAGES = [
  'Referral Submitted',
  'HR Review',
  'Eligibility Validation',
  'NDA Sent',
  'NDA Signed',
  'Joining Form Completed',
  'Non-Worker ID Creation',
  'IT Provisioning',
  'Mentor Assignment',
  'Internship Started',
  'Internship Closed',
  'Certificate Generated',
] as const;

export const SLA_THRESHOLDS_DAYS: Record<string, number> = {
  'HR Review':               2,
  'Eligibility Validation':  1,
  'NDA Sent':                1,
  'NDA Signed':              5,
  'Joining Form Completed':  3,
  'Non-Worker ID Creation':  3,
  'IT Provisioning':         5,
  'Mentor Assignment':       2,
};

export const ROLES = [
  'employee',
  'hr',
  'mentor',
  'it_admin',
  'compliance_officer',
  'program_owner',
] as const;

export const MAX_RESUME_SIZE_MB = 10;
export const ALLOWED_RESUME_TYPES = ['application/pdf'];
export const PAGE_SIZE = 20;
