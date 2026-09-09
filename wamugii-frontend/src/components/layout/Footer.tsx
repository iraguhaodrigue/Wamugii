import { Link, useLocation } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { paths } from '@/routes/paths'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'

export function Footer() {
  const year = new Date().getFullYear()
  // The homepage closes with its own full FinalCTA section, so this band would
  // be a second, weaker CTA immediately below it. Other public pages have no
  // closing CTA of their own and still need it.
  const showCtaBand = useLocation().pathname !== paths.home

  return (
    <footer className="border-t border-slate-200">
      {showCtaBand && (
      <div className="relative overflow-hidden bg-[var(--color-brand-950)]">
        <AnimatedTechBackground intensity="cta" />
        <div className="relative mx-auto flex max-w-7xl flex-col items-center gap-6 px-4 py-14 text-center sm:px-6 lg:flex-row lg:justify-between lg:text-left lg:px-8">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Ready to start your next project?
            </h2>
            <p className="mt-2 text-sm text-brand-200">
              Tell us what you need — we&apos;ll get back to you with a clear plan and a quote.
            </p>
          </div>
          <div className="flex shrink-0 flex-col gap-3 sm:flex-row">
            <Link
              to={paths.requestQuote}
              className="inline-flex h-11 items-center justify-center gap-1.5 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-5 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)]"
            >
              Request a Quote
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
            <Link
              to={paths.services}
              className="inline-flex h-11 items-center justify-center rounded-lg border border-white/20 bg-white/5 px-5 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)]"
            >
              Explore Services
            </Link>
          </div>
        </div>
      </div>
      )}

      <div className="bg-panel">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
          <div className="grid gap-10 md:grid-cols-[minmax(0,1.3fr)_repeat(3,minmax(0,1fr))]">
            <div className="max-w-sm">
              <p className="flex items-center gap-2 text-lg font-bold text-slate-900">
                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-sm font-bold text-white">
                  W
                </span>
                WAMUGII <span className="text-brand-600">TECH</span>
              </p>
              <p className="mt-3 text-sm text-slate-500">We Build. We Innovate. We Empower.</p>
              <p className="mt-2 text-sm text-slate-500">
                Web, software, IT and hosting solutions for growing businesses.
              </p>
            </div>

            {/* `contents` keeps the nav landmark for screen readers while letting
                its columns lay out as direct children of the footer grid. */}
            <nav className="contents" aria-label="Footer navigation">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Company</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-500">
                <li>
                  <Link to={paths.home} className="hover:text-brand-400">
                    Home
                  </Link>
                </li>
                <li>
                  <Link to={paths.services} className="hover:text-brand-400">
                    Services
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-900">Get started</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-500">
                <li>
                  <Link to={paths.requestQuote} className="hover:text-brand-400">
                    Request a Quote
                  </Link>
                </li>
                <li>
                  <Link to={paths.services} className="hover:text-brand-400">
                    Explore Solutions
                  </Link>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-900">Account</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-500">
                <li>
                  <Link to={paths.login} className="hover:text-brand-400">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to={paths.register} className="hover:text-brand-400">
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
