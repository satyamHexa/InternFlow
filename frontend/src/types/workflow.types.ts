// ──────────────────────────────────────────────────────────────
//  Module: src/types/workflow.types.ts
//  Responsibility: TypeScript interfaces for Workflow Engine domain.
// ──────────────────────────────────────────────────────────────

export type SLAStatus = 'on_track' | 'at_risk' | 'breached';
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'skipped';

export interface WorkflowTask {
  id: string;
  referralId: string;
  taskName: string;
  assignedTo: string;
  assignedTeam: string;
  status: TaskStatus;
  dueDate: string;
  completedAt?: string;
  slaStatus: SLAStatus;
  notes?: string;
  createdAt: string;
}

export interface WorkflowStage {
  stage: number;
  label: string;
  task?: WorkflowTask;
}

export type WorkflowStageLabel =
  | 'Referral Submitted'
  | 'HR Review'
  | 'Eligibility Validation'
  | 'NDA Sent'
  | 'NDA Signed'
  | 'Joining Form Completed'
  | 'Non-Worker ID Creation'
  | 'IT Provisioning'
  | 'Mentor Assignment'
  | 'Internship Started'
  | 'Internship Closed'
  | 'Certificate Generated';
