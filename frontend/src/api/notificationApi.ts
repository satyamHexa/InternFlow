// ──────────────────────────────────────────────────────────────
//  Module: src/api/notificationApi.ts
//  Responsibility: In-app notification reads and acknowledgement.
// ──────────────────────────────────────────────────────────────

import axiosClient from './axiosClient';
import type { Notification } from '../types/notification.types';

function mapNotification(raw: Record<string, unknown>): Notification {
  return {
    id: raw.id as string,
    userId: raw.user_id as string,
    event: raw.event as Notification['event'],
    title: raw.title as string,
    message: raw.message as string,
    isRead: raw.is_read as boolean,
    channel: raw.channel as Notification['channel'],
    referralId: raw.referral_id as string | undefined,
    createdAt: raw.created_at as string,
  };
}

const notificationApi = {
  async list(): Promise<Notification[]> {
    const { data } = await axiosClient.get<Record<string, unknown>[]>('/notifications/');
    return data.map(mapNotification);
  },

  async getUnreadCount(): Promise<number> {
    const { data } = await axiosClient.get<{ count: number }>('/notifications/unread-count');
    return data.count;
  },

  async markRead(notificationId: string): Promise<void> {
    await axiosClient.post(`/notifications/${notificationId}/read`);
  },

  async markAllRead(): Promise<void> {
    await axiosClient.post('/notifications/read-all');
  },
};

export default notificationApi;

