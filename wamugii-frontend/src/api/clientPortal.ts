import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type ClientDashboard = components['schemas']['ClientDashboardRead']
export type ClientProjectListItem = components['schemas']['ClientProjectListItem']
export type ClientProjectDetail = components['schemas']['ClientProjectDetail']
export type ClientMilestoneListItem = components['schemas']['ClientMilestoneListItem']
export type ProjectStatus = components['schemas']['ProjectStatus']

export async function getClientDashboard(): Promise<ClientDashboard> {
  const { data } = await apiClient.get<ClientDashboard>('/client/dashboard')
  return data
}

export interface ListClientProjectsParams {
  status?: ProjectStatus
  search?: string
  limit?: number
  offset?: number
}

export async function listClientProjects(params: ListClientProjectsParams = {}): Promise<ClientProjectListItem[]> {
  const { data } = await apiClient.get<ClientProjectListItem[]>('/client/projects', { params })
  return data
}

export async function getClientProject(projectId: number | string): Promise<ClientProjectDetail> {
  const { data } = await apiClient.get<ClientProjectDetail>(`/client/projects/${projectId}`)
  return data
}

export async function listClientMilestones(projectId: number | string): Promise<ClientMilestoneListItem[]> {
  const { data } = await apiClient.get<ClientMilestoneListItem[]>(`/client/projects/${projectId}/milestones`)
  return data
}
