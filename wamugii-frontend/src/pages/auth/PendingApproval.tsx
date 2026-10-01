import { Navigate } from 'react-router-dom'
import { Clock, LogOut, ShieldX } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { paths, roleHomePath } from '@/routes/paths'
import { Button, LoadingSpinner } from '@/components/ui'

/**
 * What an unapproved account sees instead of a dashboard.
 *
 * Reachable because /auth/me stays open to a PENDING account — every other
 * endpoint 403s, so there is no dashboard to render. An account that has since
 * been approved is bounced to its real home rather than left staring at this.
 */
export function PendingApproval() {
  const { user, isLoading, logout } = useAuth()

  // This route sits outside ProtectedRoute (that guard is what sends people
  // here), so it has to handle the unauthenticated and still-booting cases
  // itself rather than assume a user.
  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <LoadingSpinner size="lg" label="Checking session" />
      </div>
    )
  }
  if (!user) return <Navigate to={paths.login} replace />
  if (user.approval_status === 'APPROVED') {
    return <Navigate to={roleHomePath[user.role]} replace />
  }

  const rejected = user.approval_status === 'REJECTED'

  return (
    <div className="flex flex-col items-center gap-5 text-center">
      <div
        className={
          rejected
            ? 'flex size-12 items-center justify-center rounded-full bg-red-50 text-red-600'
            : 'flex size-12 items-center justify-center rounded-full bg-amber-50 text-amber-600'
        }
      >
        {rejected ? (
          <ShieldX className="size-6" aria-hidden="true" />
        ) : (
          <Clock className="size-6" aria-hidden="true" />
        )}
      </div>

      <div className="space-y-2">
        <h1 className="text-xl font-semibold text-slate-900">
          {rejected ? 'Registration not approved' : 'Your account is awaiting approval'}
        </h1>
        <p className="max-w-sm text-sm text-slate-500">
          {rejected
            ? "Your team member registration wasn't approved. If you think that's a mistake, get in touch with the WAMUGII team."
            : "Thanks for registering, " +
              user.full_name.split(' ')[0] +
              ". An administrator is reviewing your registration — you'll get an email as soon as it's approved, and your assigned projects will show up here."}
        </p>
      </div>

      <dl className="w-full max-w-xs space-y-2 rounded-xl border border-slate-200 bg-panel p-4 text-left text-sm">
        <div className="flex justify-between gap-3">
          <dt className="text-slate-500">Account</dt>
          <dd className="truncate font-medium text-slate-900">{user.email}</dd>
        </div>
        <div className="flex justify-between gap-3">
          <dt className="text-slate-500">Status</dt>
          <dd className="font-medium text-slate-900">
            {rejected ? 'Not approved' : 'Pending review'}
          </dd>
        </div>
      </dl>

      <Button variant="outline" leftIcon={<LogOut className="size-4" />} onClick={logout}>
        Log out
      </Button>
    </div>
  )
}
