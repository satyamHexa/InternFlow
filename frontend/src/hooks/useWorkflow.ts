// ──────────────────────────────────────────────────────────────
//  Hook: hooks/useWorkflow.ts
//  Responsibility: React Query hooks for workflow engine.
// ──────────────────────────────────────────────────────────────

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import workflowApi from '../api/workflowApi';

export function useWorkflowTasks(referralId: string) {
  return useQuery({
    queryKey: ['workflow', referralId],
    queryFn: () => workflowApi.getByReferral(referralId),
    enabled: Boolean(referralId),
  });
}

export function useMyTasks() {
  return useQuery({
    queryKey: ['workflow', 'my-tasks'],
    queryFn: workflowApi.getMyTasks,
  });
}

export function useCompleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, notes }: { taskId: string; notes?: string }) =>
      workflowApi.completeTask(taskId, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workflow'] }),
  });
}

export function useReassignTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      taskId,
      assignedTo,
      assignedTeam,
    }: {
      taskId: string;
      assignedTo: string;
      assignedTeam?: string;
    }) => workflowApi.reassignTask(taskId, assignedTo, assignedTeam),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['workflow'] }),
  });
}
