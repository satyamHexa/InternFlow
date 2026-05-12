// ──────────────────────────────────────────────────────────────
//  Page: AuditLogs.tsx
//  Route: /audit  (protected — compliance_officer, hr)
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axiosClient from '../api/axiosClient';

function useAuditLogs(page = 1) {
  return useQuery({
    queryKey: ['audit-logs', page],
    queryFn: async () => {
      const { data } = await axiosClient.get<{
        items: Array<Record<string, unknown>>;
        total: number;
        total_pages: number;
      }>('/audit/logs', { params: { page, page_size: 20 } });
      return data;
    },
  });
}

export default function AuditLogs() {
  const [page, setPage] = React.useState(1);
  const { data, isLoading } = useAuditLogs(page);

  const exportCsv = () => {
    const base = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
    window.open(`${base}/audit/logs/export/csv`, '_blank');
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Audit Logs</h1>
        <button
          onClick={exportCsv}
          className="border border-gray-300 hover:bg-gray-50 rounded-lg px-4 py-2 text-sm font-medium"
        >
          Export CSV
        </button>
      </div>

      {isLoading && <p className="text-gray-500">Loading…</p>}

      {data && (
        <div className="bg-white rounded-2xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr className="text-left text-gray-500">
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium">Module</th>
                <th className="px-4 py-3 font-medium">IP</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((log) => (
                <tr key={log.id as string} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-600">
                    {new Date(log.timestamp as string).toLocaleString()}
                  </td>
                  <td className="px-4 py-2 font-medium">{log.action as string}</td>
                  <td className="px-4 py-2 text-gray-600">{log.module as string}</td>
                  <td className="px-4 py-2 text-gray-400">{(log.ip_address as string) || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between px-4 py-3 border-t text-sm text-gray-500">
            <span>Page {page} of {data.total_pages}</span>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                className="disabled:opacity-40 border rounded px-2 py-1 hover:bg-gray-100"
              >
                ←
              </button>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage((p) => p + 1)}
                className="disabled:opacity-40 border rounded px-2 py-1 hover:bg-gray-100"
              >
                →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
