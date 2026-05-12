// ──────────────────────────────────────────────────────────────
//  Module: src/api/referralApi.ts
//  Responsibility: Referral CRUD + resume upload HTTP calls.
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';
import type { Referral, CreateReferralPayload } from '../types/referral.types';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ReferralFilters {
  page?: number;
  page_size?: number;
  status?: string;
  department?: string;
}

function mapReferral(raw: Record<string, unknown>): Referral {
  return {
    id: raw.id as string,
    candidateName: raw.candidate_name as string,
    candidateEmail: raw.candidate_email as string,
    candidatePhone: raw.candidate_phone as string,
    referrerId: raw.referrer_id as string,
    mentorId: raw.mentor_id as string | undefined,
    department: raw.department as string,
    status: raw.status as Referral['status'],
    resumeUrl: raw.resume_url as string | undefined,
    isDuplicate: raw.is_duplicate as boolean,
    createdAt: raw.created_at as string,
    updatedAt: raw.updated_at as string,
  };
}

const referralApi = {
  async create(payload: CreateReferralPayload): Promise<Referral> {
    const { data } = await axiosClient.post<Record<string, unknown>>('/referrals/', {
      candidate_name: payload.candidateName,
      candidate_email: payload.candidateEmail,
      candidate_phone: payload.candidatePhone,
      department: payload.department,
      mentor_id: payload.mentorId,
    });
    return mapReferral(data);
  },

  async list(filters: ReferralFilters = {}): Promise<PaginatedResponse<Referral>> {
    const { data } = await axiosClient.get<{
      items: Record<string, unknown>[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>('/referrals/', { params: filters });
    return {
      ...data,
      items: data.items.map(mapReferral),
    };
  },

  async getById(id: string): Promise<Referral> {
    const { data } = await axiosClient.get<Record<string, unknown>>(`/referrals/${id}`);
    return mapReferral(data);
  },

  async update(id: string, payload: Partial<CreateReferralPayload>): Promise<Referral> {
    const body: Record<string, unknown> = {};
    if (payload.candidateName) body.candidate_name = payload.candidateName;
    if (payload.candidatePhone) body.candidate_phone = payload.candidatePhone;
    if (payload.department) body.department = payload.department;
    if (payload.mentorId) body.mentor_id = payload.mentorId;
    const { data } = await axiosClient.put<Record<string, unknown>>(`/referrals/${id}`, body);
    return mapReferral(data);
  },

  async uploadResume(referralId: string, file: File): Promise<{ resumeUrl: string }> {
    const form = new FormData();
    form.append('file', file);
    const { data } = await axiosClient.post<{ resume_url: string }>(
      `/referrals/${referralId}/resume`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return { resumeUrl: data.resume_url };
  },

  async approve(referralId: string): Promise<Referral> {
    const { data } = await axiosClient.post<Record<string, unknown>>(`/referrals/${referralId}/approve`);
    return mapReferral(data);
  },

  async reject(referralId: string, reason: string): Promise<Referral> {
    const { data } = await axiosClient.post<Record<string, unknown>>(`/referrals/${referralId}/reject`, { reason });
    return mapReferral(data);
  },
};

export default referralApi;

