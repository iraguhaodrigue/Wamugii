import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type Domain = components['schemas']['DomainRead']
export type DomainListItem = components['schemas']['DomainListItem']
export type DomainCreate = components['schemas']['DomainCreate']
export type DomainUpdate = components['schemas']['DomainUpdate']
export type DomainStatus = components['schemas']['DomainStatus']

export type ClientDomainListItem = components['schemas']['ClientDomainListItem']
export type ClientDomainDetail = components['schemas']['ClientDomainDetail']

export const DOMAIN_STATUSES: DomainStatus[] = ['PENDING', 'ACTIVE', 'EXPIRED', 'CANCELLED']

/**
 * Statuses staff may choose. EXPIRED is absent because the backend rejects it —
 * it describes a date passing, not a decision.
 */
export const SETTABLE_DOMAIN_STATUSES: DomainStatus[] = ['PENDING', 'ACTIVE', 'CANCELLED']

/** Changes worth confirming before they email the client. */
export const DISRUPTIVE_DOMAIN_STATUSES: DomainStatus[] = ['CANCELLED']

export const DEFAULT_REGISTRAR = 'Namecheap'

export interface ListDomainsParams {
  status?: DomainStatus
  client_id?: number
  search?: string
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listDomains(params: ListDomainsParams = {}): Promise<DomainListItem[]> {
  const { data } = await apiClient.get<DomainListItem[]>('/domains', { params })
  return data
}

export async function getDomain(domainId: number | string): Promise<Domain> {
  const { data } = await apiClient.get<Domain>(`/domains/${domainId}`)
  return data
}

export async function createDomain(payload: DomainCreate): Promise<Domain> {
  const { data } = await apiClient.post<Domain>('/domains', payload)
  return data
}

export async function updateDomain(
  domainId: number | string,
  payload: DomainUpdate,
): Promise<Domain> {
  const { data } = await apiClient.patch<Domain>(`/domains/${domainId}`, payload)
  return data
}

export async function deactivateDomain(domainId: number | string): Promise<Domain> {
  const { data } = await apiClient.delete<Domain>(`/domains/${domainId}`)
  return data
}

// --- client portal ----------------------------------------------------------

export async function listClientDomains(): Promise<ClientDomainListItem[]> {
  const { data } = await apiClient.get<ClientDomainListItem[]>('/client/domains')
  return data
}

export async function getClientDomain(domainId: number | string): Promise<ClientDomainDetail> {
  const { data } = await apiClient.get<ClientDomainDetail>(`/client/domains/${domainId}`)
  return data
}

/**
 * Registration + service fee as a decimal string, for the invoice line item.
 * The server exposes `total_fee` on a saved domain; this mirrors it for a form
 * preview before one exists.
 */
export function totalFee(registrationFee: string, serviceFee: string | null): string {
  const total = Number(registrationFee || 0) + Number(serviceFee || 0)
  return total.toFixed(2)
}
