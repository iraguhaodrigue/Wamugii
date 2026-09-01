import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type DashboardStats = components['schemas']['DashboardStats']

export async function getAdminDashboard(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>('/admin/dashboard')
  return data
}
