import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Search, Users as UsersIcon } from 'lucide-react'
import { listAdminUsers, type Role } from '@/api/users'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  Input,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { formatDate } from '@/utils/format'
import { roleVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 15
const ROLES: Role[] = ['ADMIN', 'STAFF', 'CLIENT']

export function AdminUsers() {
  usePageTitle('Users')
  const navigate = useNavigate()

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [role, setRole] = useState<Role | ''>('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, role])

  const {
    data: users,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['admin', 'users', { role, search: debouncedSearch, page }],
    queryFn: () => listAdminUsers({ role: role || undefined, search: debouncedSearch || undefined, limit: LIMIT, offset: page * LIMIT }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(role || debouncedSearch)
  const hasNextPage = (users?.length ?? 0) === LIMIT

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">Everyone with an account on the platform.</p>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="relative sm:col-span-2">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search by name or email…"
            aria-label="Search users"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by role"
          options={[{ value: '', label: 'All roles' }, ...ROLES.map((r) => ({ value: r, label: r }))]}
          value={role}
          onChange={(e) => setRole(e.target.value as Role | '')}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-12 rounded-lg" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState title="Couldn't load users" message="We had trouble reaching the server. Please try again." onRetry={() => refetch()} />
      ) : !users || users.length === 0 ? (
        <EmptyState
          icon={UsersIcon}
          title={hasFilters ? 'No users match your filters' : 'No users yet'}
          description={hasFilters ? 'Try a different search or role.' : undefined}
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Name</TableHeaderCell>
              <TableHeaderCell>Email</TableHeaderCell>
              <TableHeaderCell>Role</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Joined</TableHeaderCell>
            </TableHead>
            <TableBody>
              {users.map((u) => (
                <TableRow key={u.id} clickable onClick={() => navigate(paths.admin.userDetail(u.id))}>
                  <TableCell className="font-medium text-slate-900">{u.full_name}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>
                    <Badge variant={roleVariant[u.role]}>{u.role}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.is_active ? 'success' : 'neutral'}>{u.is_active ? 'Active' : 'Inactive'}</Badge>
                  </TableCell>
                  <TableCell>{formatDate(u.created_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (users?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
        <div className="flex items-center justify-between border-t border-slate-200 pt-4">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="size-4" aria-hidden="true" />
            Previous
          </button>
          <span className="text-sm text-slate-500">Page {page + 1}</span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNextPage}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
            <ChevronRight className="size-4" aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  )
}
