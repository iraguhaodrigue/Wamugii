import { useEffect, useState } from 'react'
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
  const [isScrolled, setIsScrolled] = useState(false)
  const { user, isAuthenticated, logout } = useAuth()

  // Tightens the floating bar once the page scrolls, so it reads as a nav
  // rail rather than part of the hero. Passive listener, single boolean —
  // React only re-renders on the transition, not on every scroll event.
  useEffect(() => {
    function onScroll() {
      setIsScrolled(window.scrollY > 12)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={cn(
        'sticky top-0 z-40 transition-[padding] duration-300',
        isScrolled ? 'px-3 pt-2 sm:px-6 sm:pt-2' : 'px-3 pt-3 sm:px-6 sm:pt-4',
      )}
    >
      <div
        className={cn(
          'mx-auto flex max-w-6xl items-center justify-between rounded-2xl border bg-panel px-4 backdrop-blur-xl transition-[height,box-shadow,border-color] duration-300 sm:px-5',
          isScrolled
            ? 'h-12 border-brand-400/20 shadow-[var(--shadow-glow-brand)]'
            : 'h-14 border-slate-200 shadow-[var(--shadow-card)]',
        )}
      >
        <Link to={paths.home} className="flex items-center gap-2 text-base font-bold text-slate-900">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-sm font-bold text-white shadow-[var(--shadow-glow-brand)]">
            W
          </span>
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
                  'text-sm font-medium transition-colors hover:text-brand-400',
                  isActive ? 'text-brand-400' : 'text-slate-400',
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
                className="inline-flex h-9 items-center rounded-lg px-3 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-100 hover:text-white"
              >
                Dashboard
              </Link>
              <button
                type="button"
                onClick={logout}
                className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-100 hover:text-white"
              >
                <LogOut className="size-4" aria-hidden="true" />
                Logout
              </button>
            </>
          ) : (
            <Link
              to={paths.login}
              className="inline-flex h-9 items-center rounded-lg px-3 text-sm font-medium text-slate-400 transition-colors hover:bg-slate-100 hover:text-white"
            >
              Login
            </Link>
          )}
          <Link
            to={paths.requestQuote}
            className="inline-flex h-9 items-center justify-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-medium text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
          >
            Request a Quote
          </Link>
        </div>

        <button
          type="button"
          className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 md:hidden"
          aria-label={isMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMenuOpen}
          onClick={() => setIsMenuOpen((open) => !open)}
        >
          {isMenuOpen ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {isMenuOpen && (
        <nav
          className="mx-auto mt-2 max-w-6xl rounded-2xl border border-slate-200 bg-panel px-4 py-3 shadow-[var(--shadow-card)] backdrop-blur-xl md:hidden"
          aria-label="Mobile navigation"
        >
          <div className="flex flex-col gap-3">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === paths.home}
                onClick={() => setIsMenuOpen(false)}
                className={({ isActive }) =>
                  cn('text-sm font-medium', isActive ? 'text-brand-400' : 'text-slate-400')
                }
              >
                {link.label}
              </NavLink>
            ))}
            <Link
              to={paths.requestQuote}
              onClick={() => setIsMenuOpen(false)}
              className="text-sm font-medium text-slate-400"
            >
              Request a Quote
            </Link>
            {isAuthenticated ? (
              <>
                <Link
                  to={(user && roleDashboardPath[user.role]) || paths.home}
                  onClick={() => setIsMenuOpen(false)}
                  className="text-sm font-medium text-slate-400"
                >
                  Dashboard
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setIsMenuOpen(false)
                    logout()
                  }}
                  className="text-left text-sm font-medium text-slate-400"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to={paths.login}
                onClick={() => setIsMenuOpen(false)}
                className="text-sm font-medium text-slate-400"
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
