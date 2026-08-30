import { Link, Outlet } from 'react-router-dom'
import { paths } from '@/routes/paths'

export function AuthLayout() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center bg-slate-50 px-4 py-12">
      <Link to={paths.home} className="mb-8 text-xl font-bold text-slate-900">
        WAMUGII <span className="text-blue-600">TECH</span>
      </Link>
      <div className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <Outlet />
      </div>
    </div>
  )
}
