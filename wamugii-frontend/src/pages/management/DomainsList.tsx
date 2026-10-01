import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Globe, Plus, Search } from 'lucide-react'
import { DOMAIN_STATUSES, listDomains, type DomainStatus } from '@/api/domains'
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
import { CreateDomainModal } from '@/components/domains/CreateDomainModal'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { domainStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 10

export function DomainsList() {
  usePageTitle('Domains')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.domainDetail : paths.staff.domainDetail

  const { usersMap, users } = useUsersMap()

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<DomainStatus | ''>('')
  const [page, setPage] = useState(0)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status])

  const {
    data: domains,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['domains', { status, search: debouncedSearch, page }],
    queryFn: () =>
      listDomains({
        status: status || undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || debouncedSearch)
  const hasNextPage = (domains?.length ?? 0) === LIMIT

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Domains registered for clients. Billing runs through the normal invoicing flow.
        </p>
        <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
          Register Domain
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <Input
            type="search"
            placeholder="Search by domain name…"
            aria-label="Search domains"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by status"
          options={[
            { value: '', label: 'All statuses' },
            ...DOMAIN_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
          ]}
          value={status}
          onChange={(e) => setStatus(e.target.value as DomainStatus | '')}
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
          title="Couldn't load domains"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !domains || domains.length === 0 ? (
        <EmptyState
          icon={Globe}
          title={hasFilters ? 'No domains match your filters' : 'No domains yet'}
          description={
            hasFilters ? 'Try a different search or status.' : 'Register the first domain.'
          }
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Domain</TableHeaderCell>
              <TableHeaderCell>Client</TableHeaderCell>
              <TableHeaderCell>Registrar</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Expires</TableHeaderCell>
            </TableHead>
            <TableBody>
              {domains.map((domain) => (
                <TableRow key={domain.id} clickable onClick={() => navigate(detailPath(domain.id))}>
                  <TableCell className="font-medium text-slate-900">{domain.domain_name}</TableCell>
                  <TableCell>
                    {usersMap.get(domain.client_id)?.full_name ?? `#${domain.client_id}`}
                  </TableCell>
                  <TableCell>{domain.registrar}</TableCell>
                  <TableCell>
                    <Badge variant={domainStatusVariant[domain.status]}>
                      {formatEnumLabel(domain.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDate(domain.expires_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (domains?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
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

      <CreateDomainModal
        key={isCreateOpen ? 'open' : 'closed'}
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        clients={users}
        onCreated={(domain) => {
          setIsCreateOpen(false)
          navigate(detailPath(domain.id))
        }}
      />
    </div>
  )
}
