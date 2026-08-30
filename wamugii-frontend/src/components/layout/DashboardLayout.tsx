import { useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { paths } from '@/routes/paths'
import { cn } from '@/utils/cn'

export interface DashboardNavItem {
  label: string
  to: string
}

export interface DashboardLayoutProps {
  roleLabel: string
  navItems: DashboardNavItem[]
}

export function DashboardLayout({ roleLabel, navItems }: DashboardLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-svh bg-slate-50">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 shrink-0 transform border-r border-slate-200 bg-white transition-transform duration-200 md:static md:translate-x-0',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4">
          <Link to={paths.home} className="text-base font-bold text-slate-900">
            WAMUGII <span className="text-blue-600">TECH</span>
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
                  'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100',
                )
              }
              onClick={() => setIsSidebarOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/40 md:hidden"
          aria-hidden="true"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 items-center gap-3 border-b border-slate-200 bg-white px-4">
          <button
            type="button"
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Open menu"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="size-5" />
          </button>
          <span className="text-sm font-medium text-slate-500">{roleLabel}</span>
        </header>
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
