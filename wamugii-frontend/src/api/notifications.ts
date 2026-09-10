import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type NotificationRead = components['schemas']['NotificationRead']
export type NotificationType = components['schemas']['NotificationType']
export type UnreadCountRead = components['schemas']['UnreadCountRead']
export type MarkAllReadResponse = components['schemas']['MarkAllReadResponse']

export interface ListNotificationsParams {
  unread_only?: boolean
  limit?: number
  offset?: number
}

/** Newest first, scoped by the backend to the authenticated user. */
export async function listNotifications(
  params: ListNotificationsParams = {},
): Promise<NotificationRead[]> {
  const { data } = await apiClient.get<NotificationRead[]>('/notifications', { params })
  return data
}

export async function getUnreadCount(): Promise<UnreadCountRead> {
  const { data } = await apiClient.get<UnreadCountRead>('/notifications/unread-count')
  return data
}

export async function markNotificationRead(
  notificationId: number | string,
): Promise<NotificationRead> {
  const { data } = await apiClient.patch<NotificationRead>(
    `/notifications/${notificationId}/read`,
  )
  return data
}

export async function markAllNotificationsRead(): Promise<MarkAllReadResponse> {
  const { data } = await apiClient.patch<MarkAllReadResponse>('/notifications/read-all')
  return data
}
