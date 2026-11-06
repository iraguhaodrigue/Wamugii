import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from '@/context/AuthContext'
import { ThemeProvider } from '@/context/ThemeContext'
import './index.css'
import App from './App.tsx'
import { ScrollToTop } from '@/components/common/ScrollToTop'
import { listServices } from '@/api/services'
import { listPublicCourses } from '@/api/courses'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// On the home page, start the two data requests right away — in parallel with
// React's first render — instead of waiting for the sections to mount.
// The keys match Home.tsx and AIProgram.tsx, so those components reuse them.
if (window.location.pathname === '/') {
  void queryClient.prefetchQuery({ queryKey: ['services', 'home-preview'], queryFn: () => listServices() })
  void queryClient.prefetchQuery({ queryKey: ['courses', 'public'], queryFn: () => listPublicCourses() })
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ScrollToTop />
        <ThemeProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
