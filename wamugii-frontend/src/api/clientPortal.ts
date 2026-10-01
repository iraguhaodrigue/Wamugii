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

export type ClientQuoteListItem = components['schemas']['ClientQuoteListItem']
export type ClientQuoteDetail = components['schemas']['ClientQuoteDetail']
export type QuoteStatus = components['schemas']['QuoteStatus']

export interface ListClientQuotesParams {
  status?: QuoteStatus
  limit?: number
  offset?: number
}

export async function listClientQuotes(
  params: ListClientQuotesParams = {},
): Promise<ClientQuoteListItem[]> {
  const { data } = await apiClient.get<ClientQuoteListItem[]>('/client/quotes', { params })
  return data
}

/**
 * The click-through target for a QUOTE_STATUS_CHANGED notification. Scoped to
 * the signed-in client's email server-side; anything else 404s.
 */
export async function getClientQuote(quoteId: number | string): Promise<ClientQuoteDetail> {
  const { data } = await apiClient.get<ClientQuoteDetail>(`/client/quotes/${quoteId}`)
  return data
}
