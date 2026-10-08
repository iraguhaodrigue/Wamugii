import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import type { components } from '@/types/api'

type Token = components['schemas']['Token']

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api/v1`
const REFRESH_TOKEN_KEY = 'wamugii_refresh_token'

// Access token lives in memory only — never persisted to localStorage.
let accessToken: string | null = null

export function getAccessToken(): string | null {
  return accessToken
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token: string | null): void {
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

export function clearTokens(): void {
  setAccessToken(null)
  setRefreshToken(null)
}

type UnauthorizedHandler = () => void
let onUnauthorized: UnauthorizedHandler | null = null

export function setOnUnauthorized(handler: UnauthorizedHandler | null): void {
  onUnauthorized = handler
}

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`)
  }
  return config
})

// Dedupe concurrent 401s into a single refresh call instead of one per request.
let refreshPromise: Promise<string | null> | null = null

async function performRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null

  // Raw `axios`, not `apiClient`: using the configured instance would run this
  // call back through the 401 interceptor, which could retry the refresh and
  // produce the exact loop the interceptor is trying to avoid.
  try {
    const { data } = await axios.post<Token>(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
    setAccessToken(data.access_token)
    setRefreshToken(data.refresh_token)
    return data.access_token
  } catch {
    // Any failure (expired refresh token, network error, server down) resolves
    // to null; the caller treats a null as "session is over" and logs out.
    return null
  }
}

export function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = performRefresh().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

/**
 * 401 handling: exactly one silent refresh per request, then log out on failure.
 *
 * The invariants, each enforced by a specific guard:
 *   * `_retry` on the request itself -- a request that already retried once and
 *     still got 401 falls through to the rejection path, so a stale token can
 *     never cause an infinite loop.
 *   * `isAuthEndpoint` -- a 401 on /auth/login (bad credentials) or on the
 *     refresh endpoint (which `performRefresh` already handles directly) is
 *     left alone, so we never try to refresh the refresh call.
 *   * `refreshPromise` -- several concurrent 401s share one refresh call; they
 *     all see the same resolved token (or the same null) and act consistently.
 *
 * On a null from the refresh, both halves of the client-side session end:
 * tokens are cleared and `onUnauthorized` runs the registered handler
 * (AuthContext wires this to `forceLogout('expired')`, which also clears the
 * React Query cache and navigates to login with the "session expired" notice).
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequestConfig | undefined
    const url = originalRequest?.url ?? ''
    const isAuthEndpoint = url.includes('/auth/refresh') || url.includes('/auth/login')

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true

      const newAccessToken = await refreshAccessToken()
      if (newAccessToken) {
        originalRequest.headers.set('Authorization', `Bearer ${newAccessToken}`)
        return apiClient(originalRequest)
      }

      clearTokens()
      onUnauthorized?.()
    }

    return Promise.reject(normalizeError(error))
  },
)

export interface ApiError {
  status: number | null
  message: string
  detail: unknown
}

function normalizeError(error: AxiosError): ApiError {
  const status = error.response?.status ?? null
  const data = error.response?.data as { detail?: unknown } | undefined

  let message = error.message || 'Something went wrong. Please try again.'
  if (typeof data?.detail === 'string') {
    message = data.detail
  } else if (Array.isArray(data?.detail)) {
    const first = data.detail[0] as { msg?: string } | undefined
    message = first?.msg ?? message
  }

  return { status, message, detail: data?.detail }
}
