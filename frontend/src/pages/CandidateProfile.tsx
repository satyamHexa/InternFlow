// ──────────────────────────────────────────────────────────────
//  Page: CandidateProfile.tsx
//  Route: /referrals/:id  (protected)
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useReferral } from '../hooks/useReferral';
import { useWorkflowTasks } from '../hooks/useWorkflow';
import { useApproveReferral, useRejectReferral } from '../hooks/useReferral';

const STATUS_COLORS: Record<string, string> = {
  submitted: 'bg-blue-100 text-blue-800',
  hr_review: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  certificate_issued: 'bg-purple-100 text-purple-800',
};

export default function CandidateProfile() {
  const { id } = useParams<{ id: string }>();
  const { data: referral, isLoading } = useReferral(id!);
  const { data: tasks } = useWorkflowTasks(id!);
  const approve = useApproveReferral();
  const reject = useRejectReferral();

  if (isLoading) {
    return <div className="p-6 text-gray-500">Loading…</div>;
  }
  if (!referral) {
    return <div className="p-6 text-red-600">Referral not found.</div>;
  }

  const statusColor = STATUS_COLORS[referral.status] ?? 'bg-gray-100 text-gray-800';

  return (
    <div className="p-6 space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-4">
        <Link to="/" className="text-blue-600 hover:underline text-sm">← Back</Link>
        <h1 className="text-2xl font-bold text-gray-900">{referral.candidateName}</h1>
        <span className={`text-xs font-semibold px-3 py-1 rounded-full ${statusColor}`}>
          {referral.status.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="bg-white rounded-2xl shadow p-6 grid grid-cols-2 gap-4">
        <div><p className="text-xs text-gray-500">Email</p><p className="font-medium">{referral.candidateEmail}</p></div>
        <div><p className="text-xs text-gray-500">Phone</p><p className="font-medium">{referral.candidatePhone || '—'}</p></div>
        <div><p className="text-xs text-gray-500">Department</p><p className="font-medium">{referral.department}</p></div>
        <div><p className="text-xs text-gray-500">Duplicate</p><p className="font-medium">{referral.isDuplicate ? 'Yes ⚠️' : 'No'}</p></div>
        <div><p className="text-xs text-gray-500">Submitted</p><p className="font-medium">{new Date(referral.createdAt).toLocaleDateString()}</p></div>
      </div>

      {/* HR Actions */}
      {referral.status === 'submitted' && (
        <div className="flex gap-3">
          <button
            onClick={() => approve.mutate(referral.id)}
            disabled={approve.isPending}
            className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold rounded-lg px-4 py-2 text-sm"
          >
            {approve.isPending ? 'Approving…' : 'Approve'}
          </button>
          <button
            onClick={() => reject.mutate({ id: referral.id, reason: 'Does not meet requirements.' })}
            disabled={reject.isPending}
            className="bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white font-semibold rounded-lg px-4 py-2 text-sm"
          >
            {reject.isPending ? 'Rejecting…' : 'Reject'}
          </button>
        </div>
      )}

      {/* Workflow progress */}
      {tasks && tasks.length > 0 && (
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Workflow Progress</h2>
          <ol className="space-y-2">
            {tasks.map((t) => (
              <li key={t.id} className="flex items-center gap-3">
                <span
                  className={`w-5 h-5 rounded-full flex-shrink-0 ${
                    t.status === 'completed'
                      ? 'bg-green-500'
                      : t.status === 'in_progress'
                      ? 'bg-blue-500'
                      : 'bg-gray-200'
                  }`}
                />
                <span className={`text-sm ${
                  t.status === 'completed' ? 'text-gray-400 line-through' : 'text-gray-700'
                }`}>
                  {t.taskName}
                </span>
                {t.slaStatus === 'breached' && (
                  <span className="text-xs text-red-600 font-semibold">SLA Breached</span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
