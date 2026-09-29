import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type CompanySettings = components['schemas']['CompanySettingsRead']
export type CompanySettingsPublic = components['schemas']['CompanySettingsPublicRead']
export type CompanySettingsUpdate = components['schemas']['CompanySettingsUpdate']
export type InvoiceCompanyBlock = components['schemas']['InvoiceCompanyBlock']

/** Full settings including TIN and notification routing — ADMIN only. */
export async function getSettings(): Promise<CompanySettings> {
  const { data } = await apiClient.get<CompanySettings>('/settings')
  return data
}

export async function updateSettings(payload: CompanySettingsUpdate): Promise<CompanySettings> {
  const { data } = await apiClient.patch<CompanySettings>('/settings', payload)
  return data
}

/**
 * Public company info for the marketing site. The backend's response model has
 * no `tin` or `notification_email` field, so neither can arrive here.
 */
export async function getPublicSettings(): Promise<CompanySettingsPublic> {
  const { data } = await apiClient.get<CompanySettingsPublic>('/settings/public')
  return data
}
