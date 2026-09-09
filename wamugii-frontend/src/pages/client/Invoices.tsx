import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Receipt } from 'lucide-react'
import { listClientInvoices, type InvoiceStatus } from '@/api/invoices'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
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

/** Read-only view of the signed-in client's own invoices. */
export function ClientInvoices() {
  const [status, setStatus] = useState<InvoiceStatus | ''>('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    setPage(0)
  }, [status])

  const {
    data: invoices,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['client', 'invoices', { status, page }],
    queryFn: () =>
      listClientInvoices({
        status: status || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasNextPage = (invoices?.length ?? 0) === LIMIT

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Invoices</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every invoice raised for your account, with what has been paid and what is still due.
        </p>
      </div>

      <div className="sm:max-w-xs">
        <Select
          aria-label="Filter by status"
          options={[
            { value: '', label: 'All statuses' },
            ...INVOICE_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
          ]}
          value={status}
          onChange={(e) => setStatus(e.target.value as InvoiceStatus | '')}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load your invoices"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !invoices || invoices.length === 0 ? (
        <EmptyState
          icon={Receipt}
          title={status ? 'No invoices match this status' : 'No invoices yet'}
          description={
            status ? 'Try a different status.' : 'Invoices for your projects and orders will appear here.'
          }
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Invoice</TableHeaderCell>
              <TableHeaderCell>Issued</TableHeaderCell>
              <TableHeaderCell>Total</TableHeaderCell>
              <TableHeaderCell>Balance due</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Due date</TableHeaderCell>
            </TableHead>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell className="font-medium text-slate-900">
                    <Link
                      to={paths.client.invoiceDetail(invoice.id)}
                      className="hover:text-brand-600"
                    >
                      {invoice.invoice_number}
                    </Link>
                  </TableCell>
                  <TableCell>{formatDate(invoice.issue_date)}</TableCell>
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
    </div>
  )
}
