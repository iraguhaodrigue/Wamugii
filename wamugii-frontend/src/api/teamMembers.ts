import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type UserRead = components['schemas']['UserRead']
export type ApprovalStatus = components['schemas']['ApprovalStatus']
export type TeamMemberRegister = components['schemas']['TeamMemberRegister']
export type MessageResponse = components['schemas']['MessageResponse']

export type ProjectMember = components['schemas']['ProjectMemberRead']
export type ProjectMemberCreate = components['schemas']['ProjectMemberCreate']
export type ProjectMemberUpdate = components['schemas']['ProjectMemberUpdate']

// --- public self-registration ----------------------------------------------

/**
 * Creates a PENDING TEAM_MEMBER account and notifies the admins.
 *
 * Returns a message, not a user: the account can't do anything until an admin
 * approves it, and the response is deliberately the same whether or not the
 * address already had an account.
 */
export async function registerTeamMember(
  payload: TeamMemberRegister,
): Promise<MessageResponse> {
  const { data } = await apiClient.post<MessageResponse>(
    '/auth/register-team-member',
    payload,
  )
  return data
}

// --- admin approval ---------------------------------------------------------

export async function listPendingTeamMembers(): Promise<UserRead[]> {
  const { data } = await apiClient.get<UserRead[]>('/admin/team-members/pending')
  return data
}

export async function listTeamMembers(
  params: { approval_status?: ApprovalStatus } = {},
): Promise<UserRead[]> {
  const { data } = await apiClient.get<UserRead[]>('/admin/team-members', { params })
  return data
}

export async function approveTeamMember(userId: number | string): Promise<UserRead> {
  const { data } = await apiClient.patch<UserRead>(`/admin/team-members/${userId}/approve`)
  return data
}

export async function rejectTeamMember(
  userId: number | string,
  reason?: string | null,
): Promise<UserRead> {
  const { data } = await apiClient.patch<UserRead>(`/admin/team-members/${userId}/reject`, {
    reason: reason || null,
  })
  return data
}

// --- project membership (ADMIN/STAFF) --------------------------------------

export async function listProjectMembers(
  projectId: number | string,
  params: { include_inactive?: boolean } = {},
): Promise<ProjectMember[]> {
  const { data } = await apiClient.get<ProjectMember[]>(`/projects/${projectId}/members`, {
    params,
  })
  return data
}

export async function addProjectMember(
  projectId: number | string,
  payload: ProjectMemberCreate,
): Promise<ProjectMember> {
  const { data } = await apiClient.post<ProjectMember>(
    `/projects/${projectId}/members`,
    payload,
  )
  return data
}

export async function updateProjectMemberRole(
  projectId: number | string,
  memberId: number | string,
  payload: ProjectMemberUpdate,
): Promise<ProjectMember> {
  const { data } = await apiClient.patch<ProjectMember>(
    `/projects/${projectId}/members/${memberId}`,
    payload,
  )
  return data
}

export async function removeProjectMember(
  projectId: number | string,
  memberId: number | string,
): Promise<ProjectMember> {
  const { data } = await apiClient.delete<ProjectMember>(
    `/projects/${projectId}/members/${memberId}`,
  )
  return data
}
