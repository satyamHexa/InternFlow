// ──────────────────────────────────────────────────────────────
//  Page: WorkflowTracker.tsx
//  Route: /workflow/:referralId
// ──────────────────────────────────────────────────────────────

import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useWorkflowTasks, useCompleteTask } from '../hooks/useWorkflow';
import type { WorkflowTask } from '../types/workflow.types';

const SLA_BADGE: Record<string, string> = {
  on_track: 'bg-green-100 text-green-700',
  at_risk: 'bg-yellow-100 text-yellow-700',
  breached: 'bg-red-100 text-red-700',
};

function TaskRow({ task }: { task: WorkflowTask }) {
  const completeTask = useCompleteTask();
  const isActive = task.status === 'in_progress';

  return (
    <li className={`flex items-start gap-4 py-4 border-b last:border-0 ${
      isActive ? 'bg-blue-50 -mx-4 px-4 rounded-xl' : ''
    }`}>
      <div className="mt-1 flex-shrink-0">
        <span
          className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
            task.status === 'completed'
              ? 'bg-green-500 text-white'
              : isActive
              ? 'bg-blue-500 text-white'
              : 'bg-gray-200 text-gray-500'
          }`}
        >
          {task.status === 'completed' ? '✓' : task.status === 'skipped' ? '–' : String(/* stage */ '')}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 text-sm">{task.taskName}</p>
        <p className="text-xs text-gray-500">
          Team: {task.assignedTeam || '—'}
          {task.dueDate ? ` · Due ${new Date(task.dueDate).toLocaleDateString()}` : ''}
          {task.completedAt ? ` · Done ${new Date(task.completedAt).toLocaleDateString()}` : ''}
        </p>
        {task.notes && <p className="text-xs text-gray-400 mt-1 italic">{task.notes}</p>}
      </div>
      <div className="flex items-center gap-2">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
          SLA_BADGE[task.slaStatus] ?? 'bg-gray-100 text-gray-600'
        }`}>
          {task.slaStatus.replace('_', ' ')}
        </span>
        {isActive && (
          <button
            onClick={() => completeTask.mutate({ taskId: task.id })}
            disabled={completeTask.isPending}
            className="text-xs bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg px-3 py-1"
          >
            Complete
          </button>
        )}
      </div>
    </li>
  );
}

export default function WorkflowTracker() {
  const { id } = useParams<{ id: string }>();
  const { data: tasks, isLoading } = useWorkflowTasks(id!);

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Link to="/" className="text-blue-600 hover:underline text-sm">← Back</Link>
        <h1 className="text-2xl font-bold text-gray-900">Workflow Tracker</h1>
      </div>

      {isLoading && <p className="text-gray-500">Loading workflow…</p>}

      {tasks && tasks.length > 0 ? (
        <div className="bg-white rounded-2xl shadow p-4">
          <ul>
            {tasks.map((t) => <TaskRow key={t.id} task={t} />)}
          </ul>
        </div>
      ) : (
        !isLoading && <p className="text-gray-400">No workflow tasks found for this referral.</p>
      )}
    </div>
  );
}
