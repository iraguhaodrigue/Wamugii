import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { AlertTriangle, ArrowLeft, SearchX, ShieldOff } from 'lucide-react'
import { deactivateAdminUser, getAdminUser, updateAdminUser, type Role } from '@/api/users'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Select, Skeleton } from '@/components/ui'
import { formatDate } from '@/utils/format'
import { roleVariant } from '@/utils/statusBadge'

const ROLES: Role[] = ['ADMIN', 'STAFF', 'CLIENT']
const LAST_ADMIN_MESSAGE = 'Cannot remove, deactivate, or demote the last active admin'

export function AdminUserDetail() {
  const { userId } = useParams<{ userId: string }>()
  const { user: currentUser } = useAuth()
  const queryClient = useQueryClient()

  const [role, setRole] = useState<Role | null>(null)
  const [isActive, setIsActive] = useState<boolean | null>(null)
  const [isDeactivateOpen, setIsDeactivateOpen] = useState(false)
  const [lastAdminError, setLastAdminError] = useState<string | null>(null)

  const userQuery = useQuery<Awaited<ReturnType<typeof getAdminUser>>, ApiError>({
    queryKey: ['admin', 'users', 'detail', userId],
    queryFn: () => getAdminUser(userId!),
    enabled: Boolean(userId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  usePageTitle(userQuery.data?.full_name ?? 'User')

  const saveMutation = useMutation({
    mutationFn: () => updateAdminUser(userId!, { role: role ?? undefined, is_active: isActive ?? undefined }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['admin', 'users', 'detail', userId], updated)
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
      setRole(null)
      setIsActive(null)
      setLastAdminError(null)
    },
    onError: (err: ApiError) => {
      if (err.status === 409) {
        setLastAdminError(err.message)
        return
      }
      setLastAdminError(null)
    },
  })

  const deactivateMutation = useMutation({
    mutationFn: () => deactivateAdminUser(userId!),
    onSuccess: (updated) => {
      queryClient.setQueryData(['admin', 'users', 'detail', userId], updated)
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
      setIsDeactivateOpen(false)
      setLastAdminError(null)
    },
    onError: (err: ApiError) => {
      setIsDeactivateOpen(false)
      if (err.status === 409) setLastAdminError(err.message)
    },
  })

  if (userQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = userQuery.isError && userQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="User not found"
        description="This user doesn't exist."
        action={
          <Link to={paths.admin.users} className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700">
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Users
          </Link>
        }
      />
    )
  }

  if (userQuery.isError || !userQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this user"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => userQuery.refetch()}
      />
    )
  }

  const target = userQuery.data
  const currentRole = role ?? target.role
  const currentActive = isActive ?? target.is_active
  const hasChanges = (role !== null && role !== target.role) || (isActive !== null && isActive !== target.is_active)
  const isSelf = currentUser?.id === target.id

  return (
    <div className="space-y-6">
      <div>
        <Link to={paths.admin.users} className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600">
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Users
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{target.full_name}</h1>
          <Badge variant={roleVariant[target.role]}>{target.role}</Badge>
          <Badge variant={target.is_active ? 'success' : 'neutral'}>{target.is_active ? 'Active' : 'Inactive'}</Badge>
        </div>
      </div>

      {lastAdminError && (
        <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          <span>
            {lastAdminError === LAST_ADMIN_MESSAGE || lastAdminError.includes('last active admin')
              ? 'This is the last active admin account — the platform requires at least one. You cannot demote, deactivate, or remove admin access from this user until another admin exists.'
              : lastAdminError}
          </span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm lg:col-span-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Account</h2>
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">Email</dt>
              <dd className="font-medium text-slate-900">{target.email}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Phone</dt>
              <dd className="font-medium text-slate-900">{target.phone ?? 'Not set'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Joined</dt>
              <dd className="font-medium text-slate-900">{formatDate(target.created_at)}</dd>
            </div>
          </dl>

          <div className="border-t border-slate-100 pt-4">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Role &amp; access</h3>
            {isSelf && (
              <p className="mt-2 text-sm text-slate-500">This is your own account — role and status changes are still sent to the backend as normal.</p>
            )}
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Select
                label="Role"
                options={ROLES.map((r) => ({ value: r, label: r }))}
                value={currentRole}
                onChange={(e) => setRole(e.target.value as Role)}
              />
              <Select
                label="Status"
                options={[
                  { value: 'true', label: 'Active' },
                  { value: 'false', label: 'Inactive' },
                ]}
                value={String(currentActive)}
                onChange={(e) => setIsActive(e.target.value === 'true')}
              />
            </div>
            <div className="mt-4 flex justify-end">
              <Button size="sm" disabled={!hasChanges} isLoading={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
                Save Changes
              </Button>
            </div>
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-red-200 bg-red-50/50 p-6">
          <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-red-700">
            <ShieldOff className="size-4" aria-hidden="true" />
            Danger zone
          </h2>
          <p className="text-sm text-red-700">
            Deactivating this account immediately revokes their access. This does not delete their data.
          </p>
          <Button
            size="sm"
            variant="danger"
            disabled={!target.is_active}
            onClick={() => setIsDeactivateOpen(true)}
          >
            {target.is_active ? 'Deactivate Account' : 'Already Inactive'}
          </Button>
        </div>
      </div>

      <ConfirmDialog
        isOpen={isDeactivateOpen}
        onClose={() => setIsDeactivateOpen(false)}
        onConfirm={() => deactivateMutation.mutate()}
        title="Deactivate this account?"
        description={`${target.full_name} will immediately lose access to the platform.`}
        confirmLabel="Deactivate"
        isDanger
        isLoading={deactivateMutation.isPending}
      />
    </div>
  )
}
