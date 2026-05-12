// ──────────────────────────────────────────────────────────────
//  Hook: hooks/useReferral.ts
//  Responsibility: React Query hooks for referral CRUD.
// ──────────────────────────────────────────────────────────────

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import referralApi, { ReferralFilters } from '../api/referralApi';
import type { CreateReferralPayload } from '../types/referral.types';

export function useReferrals(filters: ReferralFilters = {}) {
  return useQuery({
    queryKey: ['referrals', filters],
    queryFn: () => referralApi.list(filters),
  });
}

export function useReferral(id: string) {
  return useQuery({
    queryKey: ['referrals', id],
    queryFn: () => referralApi.getById(id),
    enabled: Boolean(id),
  });
}

export function useCreateReferral() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateReferralPayload) => referralApi.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['referrals'] }),
  });
}

export function useApproveReferral() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => referralApi.approve(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['referrals'] }),
  });
}

export function useRejectReferral() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      referralApi.reject(id, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['referrals'] }),
  });
}
