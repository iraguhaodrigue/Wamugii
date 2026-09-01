import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'

export type Theme = 'light' | 'dark'

const THEME_STORAGE_KEY = 'wamugii_theme'
const DARK_SCOPE_CLASS = 'dark'

function readStoredTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    return stored === 'light' || stored === 'dark' ? stored : null
  } catch {
    return null
  }
}

function writeStoredTheme(theme: Theme): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    // Private browsing / storage disabled / quota exceeded — theme just won't persist.
  }
}

function getSystemPreference(): Theme {
  if (typeof window === 'undefined' || !window.matchMedia) return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => readStoredTheme() ?? getSystemPreference())

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === 'dark' ? 'light' : 'dark'
      writeStoredTheme(next)
      return next
    })
  }, [])

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return ctx
}

/**
 * Applies the current theme to `document.body` for as long as the calling
 * component is mounted, then removes it on unmount. Call this from a logged-
 * in shell (AdminLayout, DashboardLayout) so dark mode is scoped to "the user
 * is inside the app", never the public marketing site or auth pages — those
 * never call this hook, so the class never reaches them regardless of the
 * stored preference. Scoped to <body> rather than a wrapper div because
 * Modal/ConfirmDialog portal straight onto document.body.
 */
export function useAppShellTheme(): void {
  const { theme } = useTheme()

  useEffect(() => {
    if (theme === 'dark') {
      document.body.classList.add(DARK_SCOPE_CLASS)
    } else {
      document.body.classList.remove(DARK_SCOPE_CLASS)
    }
    return () => document.body.classList.remove(DARK_SCOPE_CLASS)
  }, [theme])
}
