// ──────────────────────────────────────────────────────────────
//  Module: src/api/certificateApi.ts
//  Responsibility: Certificate generation and download.
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';

export interface Certificate {
  id: string;
  referralId: string;
  blobUrl: string | null;
  generatedAt: string;
  generatedBy: string | null;
}

export interface CertificateDownload {
  referralId: string;
  downloadUrl: string;
  expiresInSeconds: number;
}

function mapCertificate(raw: Record<string, unknown>): Certificate {
  return {
    id: raw.id as string,
    referralId: raw.referral_id as string,
    blobUrl: raw.blob_url as string | null,
    generatedAt: raw.generated_at as string,
    generatedBy: raw.generated_by as string | null,
  };
}

const certificateApi = {
  async generate(referralId: string): Promise<Certificate> {
    const { data } = await axiosClient.post<Record<string, unknown>>('/certificates/generate', {
      referral_id: referralId,
    });
    return mapCertificate(data);
  },

  async getByReferral(referralId: string): Promise<Certificate> {
    const { data } = await axiosClient.get<Record<string, unknown>>(`/certificates/${referralId}`);
    return mapCertificate(data);
  },

  async getDownloadUrl(referralId: string): Promise<CertificateDownload> {
    const { data } = await axiosClient.get<{
      referral_id: string;
      download_url: string;
      expires_in_seconds: number;
    }>(`/certificates/${referralId}/download-url`);
    return {
      referralId: data.referral_id,
      downloadUrl: data.download_url,
      expiresInSeconds: data.expires_in_seconds,
    };
  },
};

export default certificateApi;

