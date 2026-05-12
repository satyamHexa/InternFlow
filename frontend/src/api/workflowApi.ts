// ──────────────────────────────────────────────────────────────
//  Module: src/api/workflowApi.ts
//  Responsibility: Workflow engine HTTP calls.
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';
import type { WorkflowTask } from '../types/workflow.types';

function mapTask(raw: Record<string, unknown>): WorkflowTask {
  return {
    id: raw.id as string,
    referralId: raw.referral_id as string,
    taskName: raw.task_name as string,
    assignedTo: raw.assigned_to as string,
    assignedTeam: raw.assigned_team as string,
    status: raw.status as WorkflowTask['status'],
    dueDate: raw.due_date as string,
    completedAt: raw.completed_at as string | undefined,
    slaStatus: raw.sla_status as WorkflowTask['slaStatus'],
    notes: raw.notes as string | undefined,
    createdAt: raw.created_at as string,
  };
}

const workflowApi = {
  async startWorkflow(referralId: string): Promise<{ referralId: string; tasksCreated: number }> {
    const { data } = await axiosClient.post<{ referral_id: string; tasks_created: number }>(
      `/workflow/start/${referralId}`
    );
    return { referralId: data.referral_id, tasksCreated: data.tasks_created };
  },

  async getByReferral(referralId: string): Promise<WorkflowTask[]> {
    const { data } = await axiosClient.get<Record<string, unknown>[]>(
      `/workflow/referral/${referralId}`
    );
    return data.map(mapTask);
  },

  async getMyTasks(): Promise<WorkflowTask[]> {
    const { data } = await axiosClient.get<Record<string, unknown>[]>('/workflow/tasks');
    return data.map(mapTask);
  },

  async completeTask(taskId: string, notes?: string): Promise<WorkflowTask> {
    const { data } = await axiosClient.post<Record<string, unknown>>(
      `/workflow/tasks/${taskId}/complete`,
      { notes }
    );
    return mapTask(data);
  },

  async reassignTask(taskId: string, assignedTo: string, assignedTeam?: string): Promise<WorkflowTask> {
    const { data } = await axiosClient.put<Record<string, unknown>>(
      `/workflow/tasks/${taskId}/reassign`,
      { assigned_to: assignedTo, assigned_team: assignedTeam }
    );
    return mapTask(data);
  },
};

export default workflowApi;

