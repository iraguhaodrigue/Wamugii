import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import {
  apiClient,
  clearTokens,
  getRefreshToken,
  refreshAccessToken,
  setAccessToken,
  setOnUnauthorized,
  setRefreshToken,
} from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import type { components } from '@/types/api'

export type User = components['schemas']['UserRead']
type UserCreate = components['schemas']['UserCreate']
type Token = components['schemas']['Token']

/**
 * How long a signed-in session may sit idle before we log the user out.
 *
 * A single constant so the duration is easy to change in one place. Any
 * interaction with the window (click, keypress, mouse move, scroll, touch,
 * route change) resets it; the backend's refresh-token expiry (7 days, see
 * `REFRESH_TOKEN_EXPIRE_DAYS`) is the hard upper bound.
 */
export const IDLE_TIMEOUT_MS = 30 * 60 * 1000 // 30 minutes

/** The DOM events we treat as "the user is still here". Scoped so a background
 *  tab's own ticks don't count, and so we never attach anything that fires on
 *  every pixel of mouse movement (`mousemove` is intentionally excluded). */
const ACTIVITY_EVENTS = ['mousedown', 'keydown', 'scroll', 'touchstart', 'focus'] as const

/**
 * Reasons the user ends up back at the login page.
 *
 * Carried in the navigation state so Login.tsx can show the right message.
 * `expired` fires when a silent refresh fails; `idle` from the inactivity
 * timer. A normal manual logout carries no reason.
 */
export type LogoutReason = 'expired' | 'idle'

export const LOGOUT_REASON_MESSAGES: Record<LogoutReason, string> = {
  expired: 'Your session has expired — please log in again.',
  idle: 'You were logged out due to inactivity.',
}

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<User>
  register: (data: UserCreate) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me')
  return data
}

async function requestLogin(email: string, password: string): Promise<Token> {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)
  const { data } = await apiClient.post<Token>('/auth/login', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Kept in a ref so the idle-timeout callback and the 401 handler see the
  // same up-to-date user without re-registering their listeners every render.
  const userRef = useRef<User | null>(null)
  userRef.current = user

  /**
   * The single teardown everything else routes through.
   *
   * Clears both tokens (in-memory access, localStorage refresh), resets React
   * Query so no cached user/client data lingers, drops the in-memory user,
   * and navigates to login. `reason` surfaces the right message there.
   */
  const forceLogout = useCallback(
    (reason?: LogoutReason) => {
      clearTokens()
      setUser(null)
      // `clear()` drops cache *and* observers' data. `cancelQueries` first so
      // an in-flight request can't repopulate the cache after we've cleared it.
      queryClient.cancelQueries()
      queryClient.clear()
      navigate(paths.login, { replace: true, state: reason ? { reason } : undefined })
    },
    [navigate, queryClient],
  )

  // Registered once so the axios interceptor can react to a failed silent
  // refresh without importing React Router or the query client into
  // lib/apiClient.
  useEffect(() => {
    setOnUnauthorized(() => forceLogout('expired'))
    return () => setOnUnauthorized(null)
  }, [forceLogout])

  useEffect(() => {
    async function bootstrap() {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        setIsLoading(false)
        return
      }

      const newAccessToken = await refreshAccessToken()
      if (!newAccessToken) {
        clearTokens()
        setIsLoading(false)
        return
      }

      try {
        setUser(await fetchCurrentUser())
      } catch {
        clearTokens()
      } finally {
        setIsLoading(false)
      }
    }

    bootstrap()
  }, [])

  // --- idle timeout -------------------------------------------------------
  //
  // Only runs while someone is signed in. The listener attaches once per
  // login and detaches on logout, so a signed-out tab has nothing listening.
  useEffect(() => {
    if (!user) return

    let timeoutId: number | undefined

    function schedule() {
      if (timeoutId !== undefined) window.clearTimeout(timeoutId)
      timeoutId = window.setTimeout(() => {
        if (userRef.current) forceLogout('idle')
      }, IDLE_TIMEOUT_MS)
    }

    // Each listener points at the same `schedule` so the timer always resets
    // to the full idle window on any one event, rather than racing.
    for (const event of ACTIVITY_EVENTS) {
      window.addEventListener(event, schedule, { passive: true })
    }
    schedule()

    return () => {
      if (timeoutId !== undefined) window.clearTimeout(timeoutId)
      for (const event of ACTIVITY_EVENTS) {
        window.removeEventListener(event, schedule)
      }
    }
  }, [user, forceLogout])

  async function login(email: string, password: string): Promise<User> {
    const tokens = await requestLogin(email, password)
    setAccessToken(tokens.access_token)
    setRefreshToken(tokens.refresh_token)
    const me = await fetchCurrentUser()
    setUser(me)
    return me
  }

  async function register(data: UserCreate): Promise<User> {
    await apiClient.post('/auth/register', data)
    // New accounts are always CLIENT; log in immediately for a smooth signup flow.
    return login(data.email, data.password)
  }

  function logout() {
    forceLogout()
  }

  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
