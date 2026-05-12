// ──────────────────────────────────────────────────────────────
//  Module: src/api/dashboardApi.ts
//  Responsibility: Dashboard metrics, SLA, and chart data.
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';
import type {
  DashboardMetrics,
  SLAReport,
  DepartmentReferralData,
} from '../types/dashboard.types';

function mapMetrics(raw: Record<string, unknown>): DashboardMetrics {
  return {
    totalReferrals: raw.total_referrals as number,
    pendingNDAs: raw.pending_ndas as number,
    activeInterns: raw.active_interns as number,
    slaBreaches: raw.sla_breaches as number,
    delayedOnboarding: raw.delayed_onboarding as number,
    completedThisMonth: raw.completed_this_month as number,
  };
}

function mapSLAReport(raw: Record<string, unknown>): SLAReport {
  return {
    taskName: raw.task_name as string,
    total: raw.total as number,
    onTrack: raw.on_track as number,
    atRisk: raw.at_risk as number,
    breached: raw.breached as number,
  };
}

function mapDepartmentData(raw: Record<string, unknown>): DepartmentReferralData {
  return {
    department: raw.department as string,
    count: raw.count as number,
  };
}

const dashboardApi = {
  async getMetrics(): Promise<DashboardMetrics> {
    const { data } = await axiosClient.get<Record<string, unknown>>('/dashboard/metrics');
    return mapMetrics(data);
  },

  async getSLAReport(): Promise<SLAReport[]> {
    const { data } = await axiosClient.get<Record<string, unknown>[]>('/dashboard/sla');
    return data.map(mapSLAReport);
  },

  async getReferralBreakdown(): Promise<DepartmentReferralData[]> {
    const { data } = await axiosClient.get<Record<string, unknown>[]>('/dashboard/referrals');
    return data.map(mapDepartmentData);
  },
};

export default dashboardApi;

