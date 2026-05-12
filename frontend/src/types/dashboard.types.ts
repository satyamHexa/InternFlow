// ──────────────────────────────────────────────────────────────
//  Module: src/types/dashboard.types.ts
//  Responsibility: TypeScript interfaces for Dashboard domain.
// ──────────────────────────────────────────────────────────────

export interface DashboardMetrics {
  totalReferrals: number;
  pendingNDAs: number;
  activeInterns: number;
  slaBreaches: number;
  delayedOnboarding: number;
  completedThisMonth: number;
}

export interface SLAReport {
  taskName: string;
  total: number;
  onTrack: number;
  atRisk: number;
  breached: number;
}

export interface DepartmentReferralData {
  department: string;
  count: number;
}

export interface WeeklyTrend {
  week: string;
  submitted: number;
  completed: number;
  breached: number;
}

export interface StatusFunnelData {
  stage: string;
  count: number;
}
