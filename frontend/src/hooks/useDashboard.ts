// ──────────────────────────────────────────────────────────────
//  Hook: hooks/useDashboard.ts
//  Responsibility: React Query hooks for dashboard data.
// ──────────────────────────────────────────────────────────────

import { useQuery } from '@tanstack/react-query';
import dashboardApi from '../api/dashboardApi';

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ['dashboard', 'metrics'],
    queryFn: dashboardApi.getMetrics,
    staleTime: 30_000,
  });
}

export function useSLAReport() {
  return useQuery({
    queryKey: ['dashboard', 'sla'],
    queryFn: dashboardApi.getSLAReport,
    staleTime: 60_000,
  });
}

export function useDepartmentData() {
  return useQuery({
    queryKey: ['dashboard', 'referrals'],
    queryFn: dashboardApi.getReferralBreakdown,
    staleTime: 60_000,
  });
}
