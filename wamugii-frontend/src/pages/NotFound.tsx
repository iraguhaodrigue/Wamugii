import { Link } from 'react-router-dom'
import { paths } from '@/routes/paths'

export function NotFound() {
  return (
    <div className="dark app-atmosphere flex min-h-svh flex-col items-center justify-center gap-4 px-4 text-center">
      <p className="text-sm font-semibold text-brand-400">404</p>
      <h1 className="text-2xl font-semibold text-slate-900">Page not found</h1>
      <p className="max-w-sm text-sm text-slate-500">
        The page you're looking for doesn't exist or may have been moved.
      </p>
      <Link
        to={paths.home}
        className="inline-flex h-10 items-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-medium text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
      >
        Back to home
      </Link>
    </div>
  )
}
