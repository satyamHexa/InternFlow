// ──────────────────────────────────────────────────────────────
//  Page: Certificates.tsx
//  Route: /certificates  (protected)
// ──────────────────────────────────────────────────────────────

import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import certificateApi from '../api/certificateApi';

export default function Certificates() {
  const [referralId, setReferralId] = useState('');
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

  const generate = useMutation({
    mutationFn: (id: string) => certificateApi.generate(id),
  });

  const getUrl = useMutation({
    mutationFn: (id: string) => certificateApi.getDownloadUrl(id),
    onSuccess: (data) => setDownloadUrl(data.downloadUrl),
  });

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Certificates</h1>

      <div className="bg-white rounded-2xl shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Referral ID</label>
          <input
            value={referralId}
            onChange={(e) => setReferralId(e.target.value)}
            placeholder="Paste referral UUID"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => generate.mutate(referralId)}
            disabled={!referralId || generate.isPending}
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg px-4 py-2 text-sm"
          >
            {generate.isPending ? 'Generating…' : 'Generate Certificate'}
          </button>
          <button
            onClick={() => getUrl.mutate(referralId)}
            disabled={!referralId || getUrl.isPending}
            className="flex-1 border border-gray-300 hover:bg-gray-50 rounded-lg px-4 py-2 text-sm font-medium"
          >
            Get Download URL
          </button>
        </div>

        {generate.data && (
          <div className="bg-green-50 border border-green-200 rounded-lg px-3 py-2 text-sm text-green-700">
            Certificate generated ✓
          </div>
        )}

        {downloadUrl && (
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block text-blue-600 hover:underline text-sm break-all"
          >
            {downloadUrl}
          </a>
        )}

        {(generate.error || getUrl.error) && (
          <div className="bg-red-50 border border-red-200 rounded-lg px-3 py-2 text-sm text-red-700">
            {((generate.error || getUrl.error) as Error).message}
          </div>
        )}
      </div>
    </div>
  );
}
