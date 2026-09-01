import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type ProjectFileRead = components['schemas']['ProjectFileRead']
export type ProjectFileListItem = components['schemas']['ProjectFileListItem']
export type ProjectFileUpdate = components['schemas']['ProjectFileUpdate']
export type FileCategory = components['schemas']['FileCategory']

export interface ListProjectFilesParams {
  category?: FileCategory
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listProjectFiles(
  projectId: number | string,
  params: ListProjectFilesParams = {},
): Promise<ProjectFileListItem[]> {
  const { data } = await apiClient.get<ProjectFileListItem[]>(`/projects/${projectId}/files`, { params })
  return data
}

export interface UploadProjectFilePayload {
  file: File
  category: FileCategory
  description?: string
}

export async function uploadProjectFile(
  projectId: number | string,
  payload: UploadProjectFilePayload,
): Promise<ProjectFileRead> {
  const formData = new FormData()
  formData.append('file', payload.file)
  formData.append('category', payload.category)
  if (payload.description) {
    formData.append('description', payload.description)
  }
  const { data } = await apiClient.post<ProjectFileRead>(`/projects/${projectId}/files`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function updateProjectFile(
  projectId: number | string,
  fileId: number | string,
  payload: ProjectFileUpdate,
): Promise<ProjectFileRead> {
  const { data } = await apiClient.patch<ProjectFileRead>(`/projects/${projectId}/files/${fileId}`, payload)
  return data
}

export async function deleteProjectFile(
  projectId: number | string,
  fileId: number | string,
): Promise<ProjectFileRead> {
  const { data } = await apiClient.delete<ProjectFileRead>(`/projects/${projectId}/files/${fileId}`)
  return data
}

/** Downloads require the Bearer token, so a plain <a href> won't work — fetch as a
 * blob through the authenticated client and save it client-side instead. */
export async function downloadProjectFile(
  projectId: number | string,
  fileId: number | string,
  filename: string,
): Promise<void> {
  const response = await apiClient.get(`/projects/${projectId}/files/${fileId}/download`, {
    responseType: 'blob',
  })
  const url = URL.createObjectURL(response.data as Blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
