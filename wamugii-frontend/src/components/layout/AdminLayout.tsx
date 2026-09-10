import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { LogOut, Menu, PanelLeftClose, PanelLeftOpen, X, type LucideIcon } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { useAppShellTheme } from '@/context/ThemeContext'
import { PageTitleProvider, useAdminPageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import { Avatar, ThemeToggle } from '@/components/ui'
import { NotificationBell } from '@/components/notifications/NotificationBell'
import { cn } from '@/utils/cn'

const SIDEBAR_COLLAPSED_KEY = 'wamugii_sidebar_collapsed'

function readStoredCollapsed(): boolean {
  try {
    return localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1'
  } catch {
    return false
  }
}

function writeStoredCollapsed(collapsed: boolean): void {
  try {
    localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? '1' : '0')
  } catch {
    // Private browsing / storage disabled — collapse state just won't persist.
  }
}

export interface AdminNavItem {
  label: string
  to: string
  icon: LucideIcon
  end?: boolean
}

export interface AdminLayoutProps {
  navItems: AdminNavItem[]
}

function AdminLayoutChrome({ navItems }: AdminLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(readStoredCollapsed)
  const { user, logout } = useAuth()
  const title = useAdminPageTitle()
  useAppShellTheme()

  useEffect(() => {
    writeStoredCollapsed(isCollapsed)
  }, [isCollapsed])

  return (
    <div className="app-atmosphere flex min-h-svh">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex shrink-0 transform flex-col border-r border-slate-200 bg-sidebar backdrop-blur-xl transition-[transform,width] duration-200 md:static md:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
          isCollapsed ? 'w-64 md:w-[72px]' : 'w-64',
        )}
      >
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 px-4">
          <Link
            to={paths.home}
            className={cn('flex items-center gap-2 text-base font-bold text-slate-900', isCollapsed && 'md:justify-center')}
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-sm font-bold text-white shadow-[var(--shadow-glow-brand)]">
              W
            </span>
            <span className={cn(isCollapsed && 'md:hidden')}>
              WAMUGII <span className="text-brand-600">TECH</span>
            </span>
          </Link>
          <button
            type="button"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 md:hidden"
            aria-label="Close menu"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="size-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3" aria-label="Admin navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={() => setIsSidebarOpen(false)}
              title={isCollapsed ? item.label : undefined}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg border-l-2 px-3 py-2.5 text-sm font-medium transition-colors',
                  isCollapsed && 'md:justify-center',
                  isActive
                    ? 'border-[var(--color-brand-solid)] bg-gradient-to-r from-brand-500/15 to-accent-500/10 text-brand-600'
                    : 'border-transparent text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                )
              }
            >
              <item.icon className="size-5 shrink-0" aria-hidden="true" />
              <span className={cn(isCollapsed && 'md:hidden')}>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <button
          type="button"
          onClick={() => setIsCollapsed((c) => !c)}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="hidden items-center gap-2 border-t border-slate-200 px-4 py-3 text-sm font-medium text-slate-500 hover:bg-slate-100 hover:text-slate-900 md:flex"
        >
          {isCollapsed ? <PanelLeftOpen className="size-5 shrink-0" aria-hidden="true" /> : <PanelLeftClose className="size-5 shrink-0" aria-hidden="true" />}
          <span className={cn(isCollapsed && 'md:hidden')}>Collapse</span>
        </button>

        <div className={cn('flex items-center gap-3 border-t border-slate-200 p-4', isCollapsed && 'md:justify-center')}>
          {user && <Avatar name={user.full_name} size="sm" />}
          <div className={cn('min-w-0', isCollapsed && 'md:hidden')}>
            <p className="truncate text-sm font-medium text-slate-900">{user?.full_name}</p>
            <p className="text-xs text-slate-500">{user?.role}</p>
          </div>
        </div>
      </aside>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          aria-hidden="true"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-3 border-b border-slate-200 bg-panel px-4 backdrop-blur-xl sm:px-6">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Open menu"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
          <h1 className="min-w-0 flex-1 truncate text-lg font-semibold text-slate-900">{title}</h1>
          <NotificationBell />
          <ThemeToggle />
          <div className="hidden items-center gap-3 sm:flex">
            <div className="text-right">
              <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
              <p className="text-xs text-slate-500">{user?.role}</p>
            </div>
            {user && <Avatar name={user.full_name} size="sm" />}
          </div>
          <button
            type="button"
            onClick={logout}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100"
          >
            <LogOut className="size-4" aria-hidden="true" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export function AdminLayout(props: AdminLayoutProps) {
  return (
    <PageTitleProvider>
      <AdminLayoutChrome {...props} />
    </PageTitleProvider>
  )
}
