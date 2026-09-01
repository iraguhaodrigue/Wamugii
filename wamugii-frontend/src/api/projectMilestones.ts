import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type ProjectMilestoneRead = components['schemas']['ProjectMilestoneRead']
export type ProjectMilestoneListItem = components['schemas']['ProjectMilestoneListItem']
export type ProjectMilestoneCreate = components['schemas']['ProjectMilestoneCreate']
export type ProjectMilestoneUpdate = components['schemas']['ProjectMilestoneUpdate']
export type ProjectProgressRead = components['schemas']['ProjectProgressRead']
export type MilestoneStatus = components['schemas']['MilestoneStatus']

export async function listMilestones(projectId: number | string): Promise<ProjectMilestoneListItem[]> {
  const { data } = await apiClient.get<ProjectMilestoneListItem[]>(`/projects/${projectId}/milestones`, {
    params: { limit: 500 },
  })
  return data
}

export async function createMilestone(
  projectId: number | string,
  payload: ProjectMilestoneCreate,
): Promise<ProjectMilestoneRead> {
  const { data } = await apiClient.post<ProjectMilestoneRead>(`/projects/${projectId}/milestones`, payload)
  return data
}

export async function updateMilestone(
  projectId: number | string,
  milestoneId: number | string,
  payload: ProjectMilestoneUpdate,
): Promise<ProjectMilestoneRead> {
  const { data } = await apiClient.patch<ProjectMilestoneRead>(
    `/projects/${projectId}/milestones/${milestoneId}`,
    payload,
  )
  return data
}

export async function deleteMilestone(
  projectId: number | string,
  milestoneId: number | string,
): Promise<ProjectMilestoneRead> {
  const { data } = await apiClient.delete<ProjectMilestoneRead>(
    `/projects/${projectId}/milestones/${milestoneId}`,
  )
  return data
}

export interface MilestoneReorderItem {
  id: number
  display_order: number
}

export async function reorderMilestones(
  projectId: number | string,
  milestones: MilestoneReorderItem[],
): Promise<void> {
  await apiClient.patch(`/projects/${projectId}/milestones/reorder`, { milestones })
}

export async function getProjectProgress(projectId: number | string): Promise<ProjectProgressRead> {
  const { data } = await apiClient.get<ProjectProgressRead>(`/projects/${projectId}/progress`)
  return data
}
