// ──────────────────────────────────────────────────────────────
//  Module: src/store/notificationStore.ts
//  Responsibility: In-app notification badge count and list.
// ──────────────────────────────────────────────────────────────

import { create } from 'zustand';
import type { Notification } from '../types/notification.types';

interface NotificationStore {
  notifications: Notification[];
  unreadCount: number;
  setNotifications: (items: Notification[]) => void;
  addNotification: (item: Notification) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  setUnreadCount: (count: number) => void;
  clearAll: () => void;
}

const useNotificationStore = create<NotificationStore>()((set) => ({
  notifications: [],
  unreadCount: 0,

  setNotifications: (items) =>
    set({
      notifications: items,
      unreadCount: items.filter((n) => !n.isRead).length,
    }),

  addNotification: (item) =>
    set((state) => ({
      notifications: [item, ...state.notifications],
      unreadCount: state.unreadCount + (item.isRead ? 0 : 1),
    })),

  markRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, isRead: true } : n
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, isRead: true })),
      unreadCount: 0,
    })),

  setUnreadCount: (count) => set({ unreadCount: count }),

  clearAll: () => set({ notifications: [], unreadCount: 0 }),
}));

export default useNotificationStore;

