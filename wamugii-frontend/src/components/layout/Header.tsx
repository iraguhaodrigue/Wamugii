import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { paths } from '@/routes/paths'
import { cn } from '@/utils/cn'

const navLinks = [
  { label: 'Home', to: paths.home },
  { label: 'Services', to: paths.services },
  { label: 'Request a Quote', to: paths.requestQuote },
]

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to={paths.home} className="text-lg font-bold text-slate-900">
          WAMUGII <span className="text-blue-600">TECH</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex" aria-label="Main navigation">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === paths.home}
              className={({ isActive }) =>
                cn(
                  'text-sm font-medium transition-colors hover:text-blue-600',
                  isActive ? 'text-blue-600' : 'text-slate-600',
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link
            to={paths.login}
            className="inline-flex h-8 items-center rounded-lg px-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
          >
            Login
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
        <nav
          className="border-t border-slate-200 px-4 py-3 md:hidden"
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
                  cn(
                    'text-sm font-medium',
                    isActive ? 'text-blue-600' : 'text-slate-600',
                  )
                }
              >
                {link.label}
              </NavLink>
            ))}
            <Link
              to={paths.login}
              onClick={() => setIsMenuOpen(false)}
              className="text-sm font-medium text-slate-600"
            >
              Login
            </Link>
          </div>
        </nav>
      )}
    </header>
  )
}
