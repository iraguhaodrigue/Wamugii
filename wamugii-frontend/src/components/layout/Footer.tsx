import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { paths } from '@/routes/paths'

export function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-slate-200">
      <div className="bg-gradient-to-br from-brand-900 via-brand-800 to-accent-900">
        <div className="mx-auto flex max-w-7xl flex-col items-center gap-6 px-4 py-14 text-center sm:px-6 lg:flex-row lg:justify-between lg:text-left lg:px-8">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Ready to start your next project?
            </h2>
            <p className="mt-2 text-sm text-brand-100">
              Tell us what you need — we&apos;ll get back to you with a clear plan and a quote.
            </p>
          </div>
          <div className="flex shrink-0 flex-col gap-3 sm:flex-row">
            <Link
              to={paths.requestQuote}
              className="inline-flex h-11 items-center justify-center gap-1.5 rounded-lg bg-white px-5 text-sm font-semibold text-brand-800 shadow-sm transition-colors hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-800"
            >
              Request a Quote
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
            <Link
              to={paths.services}
              className="inline-flex h-11 items-center justify-center rounded-lg border border-white/30 px-5 text-sm font-semibold text-white transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-800"
            >
              Explore Services
            </Link>
          </div>
        </div>
      </div>

      <div className="bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-8 md:flex-row md:justify-between">
            <div className="max-w-sm">
              <p className="text-lg font-bold text-slate-900">
                WAMUGII <span className="text-brand-600">TECH</span>
              </p>
              <p className="mt-2 text-sm text-slate-500">We Build. We Innovate. We Empower.</p>
            </div>

            <nav className="flex gap-8" aria-label="Footer navigation">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Company</h3>
                <ul className="mt-3 space-y-2 text-sm text-slate-500">
                  <li>
                    <Link to={paths.home} className="hover:text-brand-600">
                      Home
                    </Link>
                  </li>
                  <li>
                    <Link to={paths.services} className="hover:text-brand-600">
                      Services
                    </Link>
                  </li>
                  <li>
                    <Link to={paths.requestQuote} className="hover:text-brand-600">
                      Request a Quote
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Account</h3>
                <ul className="mt-3 space-y-2 text-sm text-slate-500">
                  <li>
                    <Link to={paths.login} className="hover:text-brand-600">
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link to={paths.register} className="hover:text-brand-600">
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
      </div>
    </footer>
  )
}
