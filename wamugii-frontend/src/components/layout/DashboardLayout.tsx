import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { LogOut, Menu, X, type LucideIcon } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { useAppShellTheme } from '@/context/ThemeContext'
import { paths } from '@/routes/paths'
import { Avatar, ThemeToggle } from '@/components/ui'
import { cn } from '@/utils/cn'

export interface DashboardNavItem {
  label: string
  to: string
  icon: LucideIcon
}

export interface DashboardLayoutProps {
  roleLabel: string
  navItems: DashboardNavItem[]
}

export function DashboardLayout({ roleLabel, navItems }: DashboardLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  useAppShellTheme()

  return (
    <div className="app-atmosphere flex min-h-svh">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 shrink-0 transform border-r border-slate-200 bg-sidebar backdrop-blur-xl transition-transform duration-200 md:static md:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4">
          <Link to={paths.home} className="flex items-center gap-2 text-base font-bold text-slate-900">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-sm font-bold text-white shadow-[var(--shadow-glow-brand)]">
              W
            </span>
            WAMUGII <span className="text-brand-600">TECH</span>
          </Link>
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Close menu"
            onClick={() => setIsSidebarOpen(false)}
          >
            <X className="size-5" />
          </button>
        </div>
        <nav className="flex flex-col gap-1 p-3" aria-label={`${roleLabel} navigation`}>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-lg border-l-2 px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-[var(--color-brand-solid)] bg-gradient-to-r from-brand-500/15 to-accent-500/10 text-brand-600'
                    : 'border-transparent text-slate-600 hover:bg-slate-100',
                )
              }
              onClick={() => setIsSidebarOpen(false)}
            >
              <item.icon className="size-5 shrink-0" aria-hidden="true" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          aria-hidden="true"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-panel px-4 backdrop-blur-xl">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Open menu"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
          <span className="text-sm font-medium text-slate-500">{roleLabel}</span>
          <div className="ml-auto flex items-center gap-3">
            <ThemeToggle />
            {user && <span className="hidden text-sm text-slate-600 sm:inline">{user.full_name}</span>}
            {user && <Avatar name={user.full_name} size="sm" />}
            <button
              type="button"
              onClick={logout}
              className="inline-flex h-8 items-center gap-1.5 rounded-lg px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100"
            >
              <LogOut className="size-4" aria-hidden="true" />
              Logout
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
