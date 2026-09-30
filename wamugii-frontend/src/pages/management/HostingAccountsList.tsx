import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Plus, Search, Server } from 'lucide-react'
import {
  HOSTING_STATUSES,
  listHostingAccounts,
  listHostingPlans,
  type HostingStatus,
} from '@/api/hosting'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
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
import { CreateHostingAccountModal } from '@/components/hosting/CreateHostingAccountModal'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { hostingStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 10

export function HostingAccountsList() {
  usePageTitle('Hosting Accounts')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.hostingAccountDetail : paths.staff.hostingAccountDetail

  const { usersMap, users } = useUsersMap()

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<HostingStatus | ''>('')
  const [planId, setPlanId] = useState('')
  const [page, setPage] = useState(0)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status, planId])

  const { data: plans } = useQuery({
    queryKey: ['hosting', 'plans', 'filter'],
    queryFn: () => listHostingPlans(true),
  })

  const {
    data: accounts,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['hosting', 'accounts', { status, planId, search: debouncedSearch, page }],
    queryFn: () =>
      listHostingAccounts({
        status: status || undefined,
        plan_id: planId ? Number(planId) : undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || planId || debouncedSearch)
  const hasNextPage = (accounts?.length ?? 0) === LIMIT
  const planName = (id: number) => (plans ?? []).find((p) => p.id === id)?.name ?? `#${id}`

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Client hosting subscriptions. Billing runs through the normal invoicing flow.
        </p>
        <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
          New Account
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <Input
            type="search"
            placeholder="Search by domain…"
            aria-label="Search hosting accounts"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by status"
          options={[
            { value: '', label: 'All statuses' },
            ...HOSTING_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
          ]}
          value={status}
          onChange={(e) => setStatus(e.target.value as HostingStatus | '')}
        />
        <Select
          aria-label="Filter by plan"
          options={[
            { value: '', label: 'All plans' },
            ...(plans ?? []).map((p) => ({ value: String(p.id), label: p.name })),
          ]}
          value={planId}
          onChange={(e) => setPlanId(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load hosting accounts"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !accounts || accounts.length === 0 ? (
        <EmptyState
          icon={Server}
          title={hasFilters ? 'No accounts match your filters' : 'No hosting accounts yet'}
          description={
            hasFilters ? 'Try a different search or filter.' : 'Create the first hosting account.'
          }
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Client</TableHeaderCell>
              <TableHeaderCell>Domain</TableHeaderCell>
              <TableHeaderCell>Plan</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Billing</TableHeaderCell>
              <TableHeaderCell>Next billing</TableHeaderCell>
              <TableHeaderCell>Expires</TableHeaderCell>
            </TableHead>
            <TableBody>
              {accounts.map((account) => (
                <TableRow
                  key={account.id}
                  clickable
                  onClick={() => navigate(detailPath(account.id))}
                >
                  <TableCell className="font-medium text-slate-900">
                    {usersMap.get(account.client_id)?.full_name ?? `#${account.client_id}`}
                  </TableCell>
                  <TableCell>
                    {account.domain ?? <span className="text-slate-500">Not set</span>}
                  </TableCell>
                  <TableCell>{planName(account.plan_id)}</TableCell>
                  <TableCell>
                    <Badge variant={hostingStatusVariant[account.status]}>
                      {formatEnumLabel(account.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatEnumLabel(account.billing_cycle)}</TableCell>
                  <TableCell>{formatDate(account.next_billing_date)}</TableCell>
                  <TableCell>{formatDate(account.expires_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (accounts?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
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

      <CreateHostingAccountModal
        key={isCreateOpen ? 'open' : 'closed'}
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        clients={users}
        onCreated={(account) => {
          setIsCreateOpen(false)
          navigate(detailPath(account.id))
        }}
      />
    </div>
  )
}
