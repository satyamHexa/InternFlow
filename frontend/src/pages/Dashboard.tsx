// ──────────────────────────────────────────────────────────────
//  Page: Dashboard.tsx
//  Route: /  (protected)
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { useDashboardMetrics, useSLAReport, useDepartmentData } from '../hooks/useDashboard';

function MetricCard({
  label,
  value,
  accent = 'blue',
}: {
  label: string;
  value: number | undefined;
  accent?: string;
}) {
  return (
    <div className={`bg-white rounded-2xl shadow p-6 border-l-4 border-${accent}-500`}>
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value ?? '—'}</p>
    </div>
  );
}

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();
  const { data: slaReport } = useSLAReport();
  const { data: departments } = useDepartmentData();

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {/* Metrics row */}
      {metricsLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-gray-200 rounded-2xl h-28" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="Total Referrals" value={metrics?.totalReferrals} accent="blue" />
          <MetricCard label="Pending NDAs" value={metrics?.pendingNDAs} accent="yellow" />
          <MetricCard label="Active Interns" value={metrics?.activeInterns} accent="green" />
          <MetricCard label="SLA Breaches" value={metrics?.slaBreaches} accent="red" />
        </div>
      )}

      {/* Department breakdown */}
      {departments && departments.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Referrals by Department</h2>
          <div className="space-y-2">
            {departments.map((d) => (
              <div key={d.department} className="flex items-center gap-3">
                <span className="w-40 text-sm text-gray-600 truncate">{d.department}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-3">
                  <div
                    className="bg-blue-500 rounded-full h-3"
                    style={{
                      width: `${Math.min(
                        100,
                        (d.count / Math.max(...departments.map((x) => x.count))) * 100
                      )}%`,
                    }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700">{d.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SLA report */}
      {slaReport && slaReport.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">SLA Status by Stage</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Stage</th>
                  <th className="pb-2 font-medium text-green-600">On Track</th>
                  <th className="pb-2 font-medium text-yellow-600">At Risk</th>
                  <th className="pb-2 font-medium text-red-600">Breached</th>
                </tr>
              </thead>
              <tbody>
                {slaReport.map((row) => (
                  <tr key={row.taskName} className="border-b last:border-0">
                    <td className="py-2 text-gray-700">{row.taskName}</td>
                    <td className="py-2 text-green-700">{row.onTrack}</td>
                    <td className="py-2 text-yellow-700">{row.atRisk}</td>
                    <td className="py-2 text-red-700">{row.breached}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

