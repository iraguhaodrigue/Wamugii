import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { LoadingSpinner } from '@/components/ui'
import { paths } from '@/routes/paths'

export function ProtectedRoute() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <LoadingSpinner size="lg" label="Checking session" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to={paths.login} replace state={{ from: location }} />
  }

  // An unapproved account can authenticate but can reach no other endpoint, so
  // every protected page would render as an error. Send it to the one screen
  // that explains why instead. The backend is still the enforcement -- this is
  // the explanation.
  if (user && user.approval_status !== 'APPROVED') {
    return <Navigate to={paths.pendingApproval} replace />
  }

  return <Outlet />
}
