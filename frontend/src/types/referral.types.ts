// ──────────────────────────────────────────────────────────────
//  Module: src/types/referral.types.ts
//  Responsibility: TypeScript interfaces for Referral domain.
// ──────────────────────────────────────────────────────────────

export type ReferralStatus =
  | 'draft'
  | 'submitted'
  | 'hr_review'
  | 'eligibility_check'
  | 'nda_pending'
  | 'nda_signed'
  | 'joining_form'
  | 'id_creation'
  | 'it_provisioning'
  | 'mentor_assigned'
  | 'active'
  | 'closed'
  | 'certificate_issued'
  | 'rejected';

export interface ParsedResume {
  fullName: string;
  email: string;
  phone: string;
  skills: string[];
  education: EducationEntry[];
  experience: ExperienceEntry[];
  confidenceScore: number;
}

export interface EducationEntry {
  institution: string;
  degree: string;
  year: string;
}

export interface ExperienceEntry {
  company: string;
  role: string;
  duration: string;
}

export interface Referral {
  id: string;
  candidateName: string;
  candidateEmail: string;
  candidatePhone: string;
  referrerId: string;
  mentorId?: string;
  department: string;
  status: ReferralStatus;
  resumeUrl?: string;
  parsedResume?: ParsedResume;
  isDuplicate: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateReferralPayload {
  candidateName: string;
  candidateEmail: string;
  candidatePhone: string;
  department: string;
  mentorId?: string;
}
