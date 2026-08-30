import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'

export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-8 md:flex-row md:justify-between">
          <div className="max-w-sm">
            <p className="text-lg font-bold text-slate-900">
              WAMUGII <span className="text-blue-600">TECH</span>
            </p>
            <p className="mt-2 text-sm text-slate-500">
              We Build. We Innovate. We Empower.
            </p>
          </div>

          <nav className="flex gap-8" aria-label="Footer navigation">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Company</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-500">
                <li>
                  <Link to={paths.home} className="hover:text-blue-600">
                    Home
                  </Link>
                </li>
                <li>
                  <Link to={paths.services} className="hover:text-blue-600">
                    Services
                  </Link>
                </li>
                <li>
                  <Link to={paths.requestQuote} className="hover:text-blue-600">
                    Request a Quote
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Account</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-500">
                <li>
                  <Link to={paths.login} className="hover:text-blue-600">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to={paths.register} className="hover:text-blue-600">
                    Register
                  </Link>
                </li>
              </ul>
            </div>
          </nav>
        </div>

        <p className="mt-8 border-t border-slate-200 pt-6 text-sm text-slate-500">
          © {year} Wamugii Tech Solutions. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
