import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type TeamProjectListItem = components['schemas']['TeamProjectListItem']
export type TeamProject = components['schemas']['TeamProjectDetail']
export type TeamProjectMilestone = components['schemas']['TeamProjectMilestone']
export type TeamProjectFile = components['schemas']['TeamProjectFile']
export type ProjectRole = components['schemas']['ProjectRole']

export const PROJECT_ROLES: ProjectRole[] = [
  'TEAM_LEAD',
  'PROGRAMMER',
  'TESTER',
  'RESEARCHER',
  'DESIGNER',
]

/**
 * The team member's own projects.
 *
 * These two endpoints are the entire surface a TEAM_MEMBER is served. The
 * payloads carry no client or billing field at all — that's enforced server-side
 * by the schemas in `app/schemas/team.py`, not here, so the frontend has nothing
 * to filter out and cannot accidentally reveal something by rendering a field.
 */
export async function listMyProjects(): Promise<TeamProjectListItem[]> {
  const { data } = await apiClient.get<TeamProjectListItem[]>('/team/projects')
  return data
}

export async function getMyProject(projectId: number | string): Promise<TeamProject> {
  const { data } = await apiClient.get<TeamProject>(`/team/projects/${projectId}`)
  return data
}

/**
 * Download a file on an assigned project.
 *
 * Same blob-through-the-authenticated-client approach as `downloadProjectFile`
 * — a plain <a href> would arrive without the Bearer token — but pointed at the
 * /team route, which scopes by membership.
 */
export async function downloadMyProjectFile(
  projectId: number | string,
  fileId: number | string,
  filename: string,
): Promise<void> {
  const response = await apiClient.get(
    `/team/projects/${projectId}/files/${fileId}/download`,
    { responseType: 'blob' },
  )
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
