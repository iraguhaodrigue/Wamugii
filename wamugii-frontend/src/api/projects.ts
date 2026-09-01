import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type ProjectRead = components['schemas']['ProjectRead']
export type ProjectListItem = components['schemas']['ProjectListItem']
export type ProjectCreate = components['schemas']['ProjectCreate']
export type ProjectUpdate = components['schemas']['ProjectUpdate']
export type ProjectStatus = components['schemas']['ProjectStatus']
export type ProjectPriority = components['schemas']['ProjectPriority']

export interface ListProjectsParams {
  status?: ProjectStatus
  priority?: ProjectPriority
  service_id?: number
  client_id?: number
  search?: string
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listProjects(params: ListProjectsParams = {}): Promise<ProjectListItem[]> {
  const { data } = await apiClient.get<ProjectListItem[]>('/projects', { params })
  return data
}

export async function getProject(projectId: number | string): Promise<ProjectRead> {
  const { data } = await apiClient.get<ProjectRead>(`/projects/${projectId}`)
  return data
}

export async function createProject(payload: ProjectCreate): Promise<ProjectRead> {
  const { data } = await apiClient.post<ProjectRead>('/projects', payload)
  return data
}

export async function updateProject(projectId: number | string, payload: ProjectUpdate): Promise<ProjectRead> {
  const { data } = await apiClient.patch<ProjectRead>(`/projects/${projectId}`, payload)
  return data
}

export async function deactivateProject(projectId: number | string): Promise<ProjectRead> {
  const { data } = await apiClient.delete<ProjectRead>(`/projects/${projectId}`)
  return data
}
