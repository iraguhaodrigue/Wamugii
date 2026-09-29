import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type ForgotPasswordRequest = components['schemas']['ForgotPasswordRequest']
export type ResetPasswordRequest = components['schemas']['ResetPasswordRequest']
export type MessageResponse = components['schemas']['MessageResponse']

/**
 * Starts a password reset. The backend answers identically whether or not the
 * address has an account, so the UI must not infer anything from a success
 * response beyond "the request was accepted".
 */
export async function forgotPassword(email: string): Promise<MessageResponse> {
  const { data } = await apiClient.post<MessageResponse>('/auth/forgot-password', { email })
  return data
}

/** Completes a reset. A 400 means the link is expired, spent, or unknown. */
export async function resetPassword(token: string, password: string): Promise<MessageResponse> {
  const { data } = await apiClient.post<MessageResponse>('/auth/reset-password', {
    token,
    password,
  })
  return data
}
