import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type QuoteRequestCreate = components['schemas']['QuoteRequestCreate']
export type QuoteRequestPublicRead = components['schemas']['QuoteRequestPublicRead']

export async function createQuoteRequest(payload: QuoteRequestCreate): Promise<QuoteRequestPublicRead> {
  const { data } = await apiClient.post<QuoteRequestPublicRead>('/quote-requests', payload)
  return data
}
