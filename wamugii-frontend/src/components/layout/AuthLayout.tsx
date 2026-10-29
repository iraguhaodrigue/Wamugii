import { Link, Outlet } from 'react-router-dom'
import { paths } from '@/routes/paths'

/** Permanently dark, same as PublicLayout — see its comment for why. */
export function AuthLayout() {
  return (
    <div className="dark app-atmosphere flex min-h-svh flex-col items-center justify-center px-4 py-12">
      <Link to={paths.home} className="mb-8 flex items-center gap-2 text-xl font-bold text-slate-900">
        <img
          src="/logo-emblem-128.png"
          alt=""
          className="size-9 shrink-0 rounded-lg object-cover shadow-[var(--shadow-glow-brand)]"
        />
        WAMUGII <span className="text-brand-600">TECH</span>
      </Link>
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-8">
        <Outlet />
      </div>
    </div>
  )
}
