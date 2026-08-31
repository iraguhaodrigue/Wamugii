import { Outlet } from 'react-router-dom'
import { ShieldAlert } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import type { components } from '@/types/api'

type Role = components['schemas']['Role']

export interface RoleProtectedRouteProps {
  allowedRoles: Role[]
}

export function RoleProtectedRoute({ allowedRoles }: RoleProtectedRouteProps) {
  const { user } = useAuth()

  if (!user || !allowedRoles.includes(user.role)) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 px-4 text-center">
        <ShieldAlert className="size-10 text-red-500" aria-hidden="true" />
        <h1 className="text-xl font-semibold text-slate-900">Not authorized</h1>
        <p className="max-w-sm text-sm text-slate-500">
          You don't have permission to view this page. Contact an administrator if you believe this is a
          mistake.
        </p>
      </div>
    )
  }

  return <Outlet />
}
