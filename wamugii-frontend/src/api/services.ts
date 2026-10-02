import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type Service = components['schemas']['ServiceRead']
export type ServiceCreate = components['schemas']['ServiceCreate']
export type ServiceUpdate = components['schemas']['ServiceUpdate']
export type ServiceQuestion = components['schemas']['ServiceQuestionRead']
export type ServiceQuestionCreate = components['schemas']['ServiceQuestionCreate']
export type ServiceQuestionUpdate = components['schemas']['ServiceQuestionUpdate']
export type QuestionType = components['schemas']['QuestionType']

export const QUESTION_TYPES: QuestionType[] = [
  'TEXT',
  'TEXTAREA',
  'NUMBER',
  'SELECT',
  'MULTISELECT',
  'YES_NO',
]

/** The only two types whose `options` list means anything — mirrors CHOICE_TYPES server-side. */
export const CHOICE_QUESTION_TYPES: QuestionType[] = ['SELECT', 'MULTISELECT']

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

// --- per-service quote questions -------------------------------------------

/**
 * A service's quote questions.
 *
 * Public: the quote form calls this when a visitor picks a service. Only active
 * questions come back unless the caller is staff and asks for the rest, so the
 * admin screen uses the same endpoint with `include_inactive`.
 */
export async function listServiceQuestions(
  serviceId: number | string,
  params: { include_inactive?: boolean } = {},
): Promise<ServiceQuestion[]> {
  const { data } = await apiClient.get<ServiceQuestion[]>(`/services/${serviceId}/questions`, {
    params,
  })
  return data
}

export async function createServiceQuestion(
  serviceId: number | string,
  payload: ServiceQuestionCreate,
): Promise<ServiceQuestion> {
  const { data } = await apiClient.post<ServiceQuestion>(
    `/services/${serviceId}/questions`,
    payload,
  )
  return data
}

export async function updateServiceQuestion(
  serviceId: number | string,
  questionId: number | string,
  payload: ServiceQuestionUpdate,
): Promise<ServiceQuestion> {
  const { data } = await apiClient.patch<ServiceQuestion>(
    `/services/${serviceId}/questions/${questionId}`,
    payload,
  )
  return data
}

/** Soft delete — submitted quotes keep their answers and the original wording. */
export async function deleteServiceQuestion(
  serviceId: number | string,
  questionId: number | string,
): Promise<ServiceQuestion> {
  const { data } = await apiClient.delete<ServiceQuestion>(
    `/services/${serviceId}/questions/${questionId}`,
  )
  return data
}

// --- service management (ADMIN/STAFF) --------------------------------------

export async function updateService(
  serviceId: number | string,
  payload: ServiceUpdate,
): Promise<Service> {
  const { data } = await apiClient.patch<Service>(`/services/${serviceId}`, payload)
  return data
}

export async function listAllServices(
  params: ListServicesParams & { include_inactive?: boolean } = {},
): Promise<Service[]> {
  const { data } = await apiClient.get<Service[]>('/services', {
    params: { limit: 100, ...params },
  })
  return data
}
