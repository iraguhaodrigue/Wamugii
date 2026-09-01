import { useEffect, useMemo, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, MessageSquare, Search } from 'lucide-react'
import { listQuoteRequests, type QuoteStatus } from '@/api/quoteRequests'
import { listServices } from '@/api/services'
import { useAuth } from '@/context/AuthContext'
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
import { formatDate, formatEnumLabel } from '@/utils/format'
import { quoteStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 10
const QUOTE_STATUSES: QuoteStatus[] = ['NEW', 'REVIEWING', 'QUOTED', 'ACCEPTED', 'REJECTED', 'CANCELLED']

export function QuotesList() {
  usePageTitle('Quote Requests')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.quoteDetail : paths.staff.quoteDetail

  const { data: services } = useQuery({ queryKey: ['services', 'filter'], queryFn: () => listServices() })
  const servicesMap = useMemo(() => new Map((services ?? []).map((s) => [s.id, s.name])), [services])

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<QuoteStatus | ''>('')
  const [serviceId, setServiceId] = useState('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status, serviceId])

  const {
    data: quotes,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['quote-requests', { status, serviceId, search: debouncedSearch, page }],
    queryFn: () =>
      listQuoteRequests({
        status: status || undefined,
        service_id: serviceId ? Number(serviceId) : undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || serviceId || debouncedSearch)
  const hasNextPage = (quotes?.length ?? 0) === LIMIT

  const statusOptions = [{ value: '', label: 'All statuses' }, ...QUOTE_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))]
  const serviceOptions = [{ value: '', label: 'All services' }, ...(services?.map((s) => ({ value: String(s.id), label: s.name })) ?? [])]

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">Quote requests submitted through the public site.</p>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search by name, email, project…"
            aria-label="Search quotes"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select aria-label="Filter by status" options={statusOptions} value={status} onChange={(e) => setStatus(e.target.value as QuoteStatus | '')} />
        <Select aria-label="Filter by service" options={serviceOptions} value={serviceId} onChange={(e) => setServiceId(e.target.value)} />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState title="Couldn't load quote requests" message="We had trouble reaching the server. Please try again." onRetry={() => refetch()} />
      ) : !quotes || quotes.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          title={hasFilters ? 'No quotes match your filters' : 'No quote requests yet'}
          description={hasFilters ? 'Try a different search or filter.' : 'Submissions from the public quote form will show up here.'}
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Project</TableHeaderCell>
              <TableHeaderCell>Contact</TableHeaderCell>
              <TableHeaderCell>Service</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Submitted</TableHeaderCell>
            </TableHead>
            <TableBody>
              {quotes.map((quote) => (
                <TableRow key={quote.id} clickable onClick={() => navigate(detailPath(quote.id))}>
                  <TableCell className="font-medium text-slate-900">{quote.project_title}</TableCell>
                  <TableCell>
                    <div>{quote.full_name}</div>
                    <div className="text-xs text-slate-500">{quote.email}</div>
                  </TableCell>
                  <TableCell>{quote.service_id ? (servicesMap.get(quote.service_id) ?? `#${quote.service_id}`) : '—'}</TableCell>
                  <TableCell>
                    <Badge variant={quoteStatusVariant[quote.status]}>{formatEnumLabel(quote.status)}</Badge>
                  </TableCell>
                  <TableCell>{formatDate(quote.created_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (quotes?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
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
