import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type QuoteRequestCreate = components['schemas']['QuoteRequestCreate']
export type QuoteRequestPublicRead = components['schemas']['QuoteRequestPublicRead']
export type QuoteRequestRead = components['schemas']['QuoteRequestRead']
export type QuoteRequestAdminUpdate = components['schemas']['QuoteRequestAdminUpdate']
export type QuoteStatus = components['schemas']['QuoteStatus']
export type ProjectRead = components['schemas']['ProjectRead']

export async function createQuoteRequest(payload: QuoteRequestCreate): Promise<QuoteRequestPublicRead> {
  const { data } = await apiClient.post<QuoteRequestPublicRead>('/quote-requests', payload)
  return data
}

// --- ADMIN / STAFF management (backend-role-gated; these calls simply surface
// whatever the backend allows or rejects) ---

export interface ListQuoteRequestsParams {
  status?: QuoteStatus
  service_id?: number
  search?: string
  limit?: number
  offset?: number
}

export async function listQuoteRequests(params: ListQuoteRequestsParams = {}): Promise<QuoteRequestRead[]> {
  const { data } = await apiClient.get<QuoteRequestRead[]>('/quote-requests', { params })
  return data
}

export async function getQuoteRequest(quoteId: number | string): Promise<QuoteRequestRead> {
  const { data } = await apiClient.get<QuoteRequestRead>(`/quote-requests/${quoteId}`)
  return data
}

export async function updateQuoteRequest(
  quoteId: number | string,
  payload: QuoteRequestAdminUpdate,
): Promise<QuoteRequestRead> {
  const { data } = await apiClient.patch<QuoteRequestRead>(`/quote-requests/${quoteId}`, payload)
  return data
}

export async function deleteQuoteRequest(quoteId: number | string): Promise<QuoteRequestRead> {
  const { data } = await apiClient.delete<QuoteRequestRead>(`/quote-requests/${quoteId}`)
  return data
}

export async function convertQuoteToProject(
  quoteId: number | string,
  clientId?: number,
): Promise<ProjectRead> {
  const { data } = await apiClient.post<ProjectRead>(`/quote-requests/${quoteId}/create-project`, null, {
    params: clientId ? { client_id: clientId } : undefined,
  })
  return data
}
