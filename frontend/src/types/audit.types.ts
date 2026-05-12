// ──────────────────────────────────────────────────────────────
//  Module: src/types/audit.types.ts
// ──────────────────────────────────────────────────────────────

export type AuditAction =
  | 'form_edit'
  | 'ai_override'
  | 'nda_download'
  | 'access_provision'
  | 'workflow_transition'
  | 'login'
  | 'logout'
  | 'role_change';

export interface AuditLog {
  id: string;
  userId: string;
  userName: string;
  action: AuditAction;
  module: string;
  metadata: Record<string, unknown>;
  timestamp: string;
  ipAddress?: string;
}
