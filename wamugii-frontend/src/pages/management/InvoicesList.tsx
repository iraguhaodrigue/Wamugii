import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Plus, Receipt, Search } from 'lucide-react'
import { listInvoices, type InvoiceStatus } from '@/api/invoices'
import { listProjects } from '@/api/projects'
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
import { CreateInvoiceModal } from '@/components/invoices/CreateInvoiceModal'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { invoiceStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 10

const INVOICE_STATUSES: InvoiceStatus[] = [
  'DRAFT',
  'SENT',
  'PARTIALLY_PAID',
  'PAID',
  'OVERDUE',
  'CANCELLED',
]

export function InvoicesList() {
  usePageTitle('Invoices')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.invoiceDetail : paths.staff.invoiceDetail

  const { usersMap, users } = useUsersMap()

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<InvoiceStatus | ''>('')
  const [clientId, setClientId] = useState('')
  const [projectId, setProjectId] = useState('')
  const [page, setPage] = useState(0)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status, clientId, projectId])

  const { data: projects } = useQuery({
    queryKey: ['projects', 'invoice-filter'],
    queryFn: () => listProjects({ limit: 100 }),
  })

  const {
    data: invoices,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['invoices', { status, clientId, projectId, search: debouncedSearch, page }],
    queryFn: () =>
      listInvoices({
        status: status || undefined,
        client_id: clientId ? Number(clientId) : undefined,
        project_id: projectId ? Number(projectId) : undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || clientId || projectId || debouncedSearch)
  // Same convention as the other list screens: a full page means there may be more.
  const hasNextPage = (invoices?.length ?? 0) === LIMIT

  const statusOptions = [
    { value: '', label: 'All statuses' },
    ...INVOICE_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
  ]
  const clientOptions = [
    { value: '', label: 'All clients' },
    ...users.filter((u) => u.role === 'CLIENT').map((u) => ({ value: String(u.id), label: u.full_name })),
  ]
  const projectOptions = [
    { value: '', label: 'All projects' },
    ...(projects ?? []).map((p) => ({ value: String(p.id), label: p.title })),
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Invoices raised for clients — linked to a project, or standalone.
        </p>
        <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
          New Invoice
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <Input
            type="search"
            placeholder="Search by invoice number…"
            aria-label="Search invoices"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by status"
          options={statusOptions}
          value={status}
          onChange={(e) => setStatus(e.target.value as InvoiceStatus | '')}
        />
        <Select
          aria-label="Filter by client"
          options={clientOptions}
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
        />
        <Select
          aria-label="Filter by project"
          options={projectOptions}
          value={projectId}
          onChange={(e) => setProjectId(e.target.value)}
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
          title="Couldn't load invoices"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !invoices || invoices.length === 0 ? (
        <EmptyState
          icon={Receipt}
          title={hasFilters ? 'No invoices match your filters' : 'No invoices yet'}
          description={
            hasFilters ? 'Try a different search or filter.' : 'Create the first invoice to get started.'
          }
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Invoice</TableHeaderCell>
              <TableHeaderCell>Client</TableHeaderCell>
              <TableHeaderCell>Project</TableHeaderCell>
              <TableHeaderCell>Total</TableHeaderCell>
              <TableHeaderCell>Balance due</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Due date</TableHeaderCell>
            </TableHead>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow
                  key={invoice.id}
                  clickable
                  onClick={() => navigate(detailPath(invoice.id))}
                >
                  <TableCell className="font-medium text-slate-900">{invoice.invoice_number}</TableCell>
                  <TableCell>
                    {usersMap.get(invoice.client_id)?.full_name ?? `#${invoice.client_id}`}
                  </TableCell>
                  <TableCell>
                    {invoice.project_id ? (
                      (projects ?? []).find((p) => p.id === invoice.project_id)?.title ??
                      `#${invoice.project_id}`
                    ) : (
                      <span className="text-slate-500">Standalone</span>
                    )}
                  </TableCell>
                  <TableCell>{formatMoney(invoice.total) ?? '—'}</TableCell>
                  <TableCell className="font-medium text-slate-900">
                    {formatMoney(invoice.balance_due) ?? '—'}
                  </TableCell>
                  <TableCell>
                    <Badge variant={invoiceStatusVariant[invoice.status]}>
                      {formatEnumLabel(invoice.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDate(invoice.due_date)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (invoices?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
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

      <CreateInvoiceModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        clients={users}
        onCreated={(invoice) => {
          setIsCreateOpen(false)
          navigate(detailPath(invoice.id))
        }}
      />
    </div>
  )
}
