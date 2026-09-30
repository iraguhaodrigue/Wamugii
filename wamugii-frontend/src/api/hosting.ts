import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type HostingPlan = components['schemas']['HostingPlanRead']
export type HostingPlanCreate = components['schemas']['HostingPlanCreate']
export type HostingPlanUpdate = components['schemas']['HostingPlanUpdate']
export type HostingAccount = components['schemas']['HostingAccountRead']
export type HostingAccountListItem = components['schemas']['HostingAccountListItem']
export type HostingAccountCreate = components['schemas']['HostingAccountCreate']
export type HostingAccountUpdate = components['schemas']['HostingAccountUpdate']
export type HostingStatus = components['schemas']['HostingStatus']
export type BillingCycle = components['schemas']['BillingCycle']

export type ClientHostingListItem = components['schemas']['ClientHostingListItem']
export type ClientHostingDetail = components['schemas']['ClientHostingDetail']

export const HOSTING_STATUSES: HostingStatus[] = [
  'PENDING',
  'ACTIVE',
  'SUSPENDED',
  'EXPIRED',
  'CANCELLED',
]

/**
 * Statuses an admin/staff member may choose. EXPIRED is absent because the
 * backend rejects it — it describes a date passing, not a decision.
 */
export const SETTABLE_HOSTING_STATUSES: HostingStatus[] = [
  'PENDING',
  'ACTIVE',
  'SUSPENDED',
  'CANCELLED',
]

/** Changes worth a confirmation step before they fire a client email. */
export const DISRUPTIVE_STATUSES: HostingStatus[] = ['SUSPENDED', 'CANCELLED']

export const BILLING_CYCLES: BillingCycle[] = ['MONTHLY', 'YEARLY']

// --- plans (public read, admin write) ---------------------------------------

export async function listHostingPlans(includeInactive = false): Promise<HostingPlan[]> {
  const { data } = await apiClient.get<HostingPlan[]>('/hosting/plans', {
    params: { include_inactive: includeInactive },
  })
  return data
}

export async function getHostingPlan(planId: number | string): Promise<HostingPlan> {
  const { data } = await apiClient.get<HostingPlan>(`/hosting/plans/${planId}`)
  return data
}

export async function createHostingPlan(payload: HostingPlanCreate): Promise<HostingPlan> {
  const { data } = await apiClient.post<HostingPlan>('/hosting/plans', payload)
  return data
}

export async function updateHostingPlan(
  planId: number | string,
  payload: HostingPlanUpdate,
): Promise<HostingPlan> {
  const { data } = await apiClient.patch<HostingPlan>(`/hosting/plans/${planId}`, payload)
  return data
}

export async function deactivateHostingPlan(planId: number | string): Promise<HostingPlan> {
  const { data } = await apiClient.delete<HostingPlan>(`/hosting/plans/${planId}`)
  return data
}

// --- accounts (admin/staff) -------------------------------------------------

export interface ListHostingAccountsParams {
  status?: HostingStatus
  plan_id?: number
  client_id?: number
  search?: string
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listHostingAccounts(
  params: ListHostingAccountsParams = {},
): Promise<HostingAccountListItem[]> {
  const { data } = await apiClient.get<HostingAccountListItem[]>('/hosting/accounts', { params })
  return data
}

export async function getHostingAccount(accountId: number | string): Promise<HostingAccount> {
  const { data } = await apiClient.get<HostingAccount>(`/hosting/accounts/${accountId}`)
  return data
}

export async function createHostingAccount(
  payload: HostingAccountCreate,
): Promise<HostingAccount> {
  const { data } = await apiClient.post<HostingAccount>('/hosting/accounts', payload)
  return data
}

export async function updateHostingAccount(
  accountId: number | string,
  payload: HostingAccountUpdate,
): Promise<HostingAccount> {
  const { data } = await apiClient.patch<HostingAccount>(`/hosting/accounts/${accountId}`, payload)
  return data
}

export async function deactivateHostingAccount(
  accountId: number | string,
): Promise<HostingAccount> {
  const { data } = await apiClient.delete<HostingAccount>(`/hosting/accounts/${accountId}`)
  return data
}

// --- client portal ----------------------------------------------------------

export async function listClientHosting(): Promise<ClientHostingListItem[]> {
  const { data } = await apiClient.get<ClientHostingListItem[]>('/client/hosting')
  return data
}

export async function getClientHosting(accountId: number | string): Promise<ClientHostingDetail> {
  const { data } = await apiClient.get<ClientHostingDetail>(`/client/hosting/${accountId}`)
  return data
}

// --- helpers ----------------------------------------------------------------

/** Mirrors crud.hosting.compute_next_billing_date for the form preview only. */
export function previewNextBillingDate(startDate: string, cycle: BillingCycle): string | null {
  if (!startDate) return null
  const [y, m, d] = startDate.split('-').map(Number)
  if (!y || !m || !d) return null

  const monthsToAdd = cycle === 'YEARLY' ? 12 : 1
  const targetIndex = m - 1 + monthsToAdd
  const year = y + Math.floor(targetIndex / 12)
  const month = (targetIndex % 12) + 1
  // Clamp to the target month's length, as the server does — 31 Jan + 1 month
  // lands on the end of February, it doesn't roll into March.
  const lastDay = new Date(Date.UTC(year, month, 0)).getUTCDate()
  const day = Math.min(d, lastDay)
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

/** The price that applies for a given cycle, as a decimal string. */
export function priceForCycle(plan: HostingPlan, cycle: BillingCycle): string {
  return cycle === 'YEARLY' ? plan.yearly_price : plan.monthly_price
}
