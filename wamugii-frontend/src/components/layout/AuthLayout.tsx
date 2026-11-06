import { Suspense } from 'react'
import { PageLoader } from '@/components/common/PageLoader'
import { Link, Outlet } from 'react-router-dom'
import { paths } from '@/routes/paths'
import { ThemeToggle } from '@/components/ui'
import { AuthArt } from '@/components/common/PageArt'
import { useAppShellTheme, useTheme } from '@/context/ThemeContext'
import { cn } from '@/utils/cn'

/**
 * Login, register and password pages. Follows the site theme (see
 * PublicLayout). On large screens the form sits beside an always-dark panel
 * with an animated "your client portal" illustration; on phones it is just the
 * form, so nothing gets in the way of signing in.
 */
export function AuthLayout() {
  const { theme } = useTheme()
  useAppShellTheme()
  return (
    <div className={cn(theme === 'dark' && 'dark', 'app-atmosphere relative flex min-h-svh items-center justify-center px-4 py-12')}>
      <ThemeToggle className="absolute right-4 top-4" />
      <div className="grid w-full max-w-5xl items-center gap-10 lg:grid-cols-2">
        <div className="dark relative hidden overflow-hidden rounded-3xl border border-white/10 bg-[var(--color-brand-950)] p-10 shadow-[var(--shadow-glow-brand)] lg:block">
          <div
            className="pointer-events-none absolute inset-0 bg-cover bg-center opacity-60"
            style={{ backgroundImage: "url('/graphics/gradient-blobs.svg')" }}
            aria-hidden="true"
          />
          <div className="relative">
            <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">Client portal</p>
            <h2 className="mt-2 text-3xl font-extrabold leading-tight text-white">
              Everything about your project, <span className="text-gradient-hero">in one place.</span>
            </h2>
            <div className="mt-8">
              <AuthArt />
            </div>
          </div>
        </div>

        <div className="hero-in mx-auto w-full max-w-md">
          <Link to={paths.home} className="mb-8 flex items-center justify-center gap-2 text-xl font-bold text-slate-900">
            <img
              src="/logo-emblem-128.png"
              alt=""
              className="size-9 shrink-0 rounded-lg object-cover shadow-[var(--shadow-glow-brand)]"
            />
            WAMUGII <span className="text-brand-600">TECH</span>
          </Link>
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-8">
            <Suspense fallback={<PageLoader />}>
            <Outlet />
          </Suspense>
          </div>
        </div>
      </div>
    </div>
  )
}
