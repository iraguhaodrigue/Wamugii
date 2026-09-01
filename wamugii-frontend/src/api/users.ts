import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type UserRead = components['schemas']['UserRead']
export type UserAdminUpdate = components['schemas']['UserAdminUpdate']
export type Role = components['schemas']['Role']

/** GET /users — available to any STAFF or ADMIN, used for id -> name lookups. */
export async function listUsers(): Promise<UserRead[]> {
  const { data } = await apiClient.get<UserRead[]>('/users')
  return data
}

// --- ADMIN-only user management (/admin/users) ---

export interface ListAdminUsersParams {
  search?: string
  role?: Role
  limit?: number
  offset?: number
}

export async function listAdminUsers(params: ListAdminUsersParams = {}): Promise<UserRead[]> {
  const { data } = await apiClient.get<UserRead[]>('/admin/users', { params })
  return data
}

export async function getAdminUser(userId: number | string): Promise<UserRead> {
  const { data } = await apiClient.get<UserRead>(`/admin/users/${userId}`)
  return data
}

export async function updateAdminUser(userId: number | string, payload: UserAdminUpdate): Promise<UserRead> {
  const { data } = await apiClient.patch<UserRead>(`/admin/users/${userId}`, payload)
  return data
}

export async function deactivateAdminUser(userId: number | string): Promise<UserRead> {
  const { data } = await apiClient.delete<UserRead>(`/admin/users/${userId}`)
  return data
}
