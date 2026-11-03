import { Outlet } from 'react-router-dom'
import { AnnouncementBar } from './AnnouncementBar'
import { Header } from './Header'
import { Footer } from './Footer'
import { ChatWidget } from '@/components/common/ChatWidget'
import { useAppShellTheme, useTheme } from '@/context/ThemeContext'
import { cn } from '@/utils/cn'

/**
 * The public site follows the same light/dark theme as the dashboards (the
 * sun/moon button in the Header), dark by default. `.dark` on the wrapper
 * (and on <body>, for anything portalled) remaps every `bg-panel` /
 * `text-slate-*` / `bg-brand-*` token, so components need no `dark:`
 * variants. Sections that are designed as dark "bands" (hero, CTA panels)
 * carry their own `dark` class and stay dark in both themes.
 */
export function PublicLayout() {
  const { theme } = useTheme()
  useAppShellTheme()
  return (
    <div className={cn(theme === 'dark' && 'dark', 'app-atmosphere flex min-h-svh flex-col text-slate-500')}>
      <AnnouncementBar />
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      {/* Public pages only — the authenticated shells (AdminLayout,
          DashboardLayout) don't mount this. */}
      <ChatWidget />
    </div>
  )
}
