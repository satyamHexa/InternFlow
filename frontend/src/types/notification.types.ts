// ──────────────────────────────────────────────────────────────
//  Module: src/types/notification.types.ts
// ──────────────────────────────────────────────────────────────

export type NotificationChannel = 'email' | 'teams' | 'in_app';
export type NotificationEvent =
  | 'referral_submitted'
  | 'nda_pending'
  | 'nda_signed'
  | 'sla_breach'
  | 'certificate_ready'
  | 'intern_start_reminder'
  | 'task_assigned';

export interface Notification {
  id: string;
  userId: string;
  event: NotificationEvent;
  title: string;
  message: string;
  isRead: boolean;
  channel: NotificationChannel;
  referralId?: string;
  createdAt: string;
}
