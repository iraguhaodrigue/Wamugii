import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
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

  // Registered once so the axios interceptor can react to a failed silent
  // refresh without importing React Router internals into lib/apiClient.
  useEffect(() => {
    setOnUnauthorized(() => {
      setUser(null)
      navigate(paths.login, { replace: true })
    })
    return () => setOnUnauthorized(null)
  }, [navigate])

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
    clearTokens()
    setUser(null)
    navigate(paths.login, { replace: true })
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
