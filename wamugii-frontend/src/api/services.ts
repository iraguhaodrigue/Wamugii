import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type Service = components['schemas']['ServiceRead']

export interface ListServicesParams {
  category?: string
  search?: string
}

export async function listServices(params: ListServicesParams = {}): Promise<Service[]> {
  const { data } = await apiClient.get<Service[]>('/services', {
    params: { limit: 100, ...params },
  })
  return data
}

export async function getService(serviceId: number | string): Promise<Service> {
  const { data } = await apiClient.get<Service>(`/services/${serviceId}`)
  return data
}
