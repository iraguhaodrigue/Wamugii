import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

interface PageTitleContextValue {
  title: string
  setTitle: (title: string) => void
}

const PageTitleContext = createContext<PageTitleContextValue | undefined>(undefined)

export function PageTitleProvider({ children }: { children: ReactNode }) {
  const [title, setTitle] = useState('')
  return <PageTitleContext.Provider value={{ title, setTitle }}>{children}</PageTitleContext.Provider>
}

function usePageTitleContext(): PageTitleContextValue {
  const ctx = useContext(PageTitleContext)
  if (!ctx) {
    throw new Error('usePageTitleContext must be used within a PageTitleProvider')
  }
  return ctx
}

/** Lets a routed page announce its title to the enclosing AdminLayout top bar. */
export function usePageTitle(title: string): void {
  const { setTitle } = usePageTitleContext()
  useEffect(() => {
    setTitle(title)
  }, [title, setTitle])
}

export function useAdminPageTitle(): string {
  return usePageTitleContext().title
}
