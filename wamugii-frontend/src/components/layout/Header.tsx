import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { LogOut, Menu, X } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { paths } from '@/routes/paths'
import { cn } from '@/utils/cn'

const navLinks = [
  { label: 'Home', to: paths.home },
  { label: 'Services', to: paths.services },
]

const roleDashboardPath: Record<string, string> = {
  ADMIN: paths.admin.dashboard,
  STAFF: paths.staff.overview,
  CLIENT: paths.client.dashboard,
}

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/85 backdrop-blur supports-[backdrop-filter]:bg-white/70">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to={paths.home} className="text-lg font-bold text-slate-900">
          WAMUGII <span className="text-brand-600">TECH</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex" aria-label="Main navigation">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === paths.home}
              className={({ isActive }) =>
                cn(
                  'text-sm font-medium transition-colors hover:text-brand-600',
                  isActive ? 'text-brand-600' : 'text-slate-600',
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated ? (
            <>
              <Link
                to={(user && roleDashboardPath[user.role]) || paths.home}
                className="inline-flex h-9 items-center rounded-lg px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
              >
                Dashboard
              </Link>
              <button
                type="button"
                onClick={logout}
                className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100"
              >
                <LogOut className="size-4" aria-hidden="true" />
                Logout
              </button>
            </>
          ) : (
            <Link
              to={paths.login}
              className="inline-flex h-9 items-center rounded-lg px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
            >
              Login
            </Link>
          )}
          <Link
            to={paths.requestQuote}
            className="inline-flex h-9 items-center justify-center rounded-lg bg-brand-600 px-4 text-sm font-medium text-white shadow-sm shadow-brand-900/10 transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
          >
            Request a Quote
          </Link>
        </div>

        <button
          type="button"
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
          aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((open) => !open)}
        >
          {isMenuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {isMenuOpen && (
        <nav className="border-t border-slate-200 px-4 py-3 md:hidden" aria-label="Mobile navigation">
          <div className="flex flex-col gap-3">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === paths.home}
                onClick={() => setIsMenuOpen(false)}
                className={({ isActive }) =>
                  cn('text-sm font-medium', isActive ? 'text-brand-600' : 'text-slate-600')
                }
              >
                {link.label}
              </NavLink>
            ))}
            <Link
              to={paths.requestQuote}
              onClick={() => setIsMenuOpen(false)}
              className="text-sm font-medium text-slate-600"
            >
              Request a Quote
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  to={(user && roleDashboardPath[user.role]) || paths.home}
                  onClick={() => setIsMenuOpen(false)}
                  className="text-sm font-medium text-slate-600"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setIsMenuOpen(false)
                    logout()
                  }}
                  className="text-left text-sm font-medium text-slate-600"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to={paths.login}
                onClick={() => setIsMenuOpen(false)}
                className="text-sm font-medium text-slate-600"
              >
                Login
              </Link>
            )}
          </div>
        </nav>
      )}
    </header>
  )
}
