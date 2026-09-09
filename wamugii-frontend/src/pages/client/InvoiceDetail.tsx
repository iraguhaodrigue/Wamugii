import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Printer, SearchX } from 'lucide-react'
import { getClientInvoice, type ClientInvoiceDetail as ClientInvoiceDetailType } from '@/api/invoices'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { invoiceStatusVariant } from '@/utils/statusBadge'

/**
 * Read-only client view. The payload comes from /client/invoices/{id}, which
 * the backend scopes to the signed-in client and which omits staff-facing
 * notes entirely — there is nothing to filter out here.
 */
export function ClientInvoiceDetail() {
  const { invoiceId } = useParams<{ invoiceId: string }>()

  const invoiceQuery = useQuery<ClientInvoiceDetailType, ApiError>({
    queryKey: ['client', 'invoices', 'detail', invoiceId],
    queryFn: () => getClientInvoice(invoiceId!),
    enabled: Boolean(invoiceId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  if (invoiceQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = invoiceQuery.isError && invoiceQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Invoice not found"
        description="This invoice doesn't exist or isn't linked to your account."
        action={
          <Link
            to={paths.client.invoices}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to My Invoices
          </Link>
        }
      />
    )
  }

  if (invoiceQuery.isError || !invoiceQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this invoice"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => invoiceQuery.refetch()}
      />
    )
  }

  const invoice = invoiceQuery.data

  return (
    <div className="space-y-6">
      <div className="print:hidden">
        <Link
          to={paths.client.invoices}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Invoices
        </Link>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{invoice.invoice_number}</h1>
          <Badge variant={invoiceStatusVariant[invoice.status]}>{formatEnumLabel(invoice.status)}</Badge>
        </div>
        {/* Prints the page as-is — no document is generated or sent anywhere. */}
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Printer className="size-4" />}
          onClick={() => window.print()}
          className="print:hidden"
        >
          Print
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Line items</h2>
            {invoice.items.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">No itemised lines on this invoice.</p>
            ) : (
              <ul className="mt-4 divide-y divide-slate-100">
                {invoice.items.map((item) => (
                  <li key={item.id} className="flex items-start justify-between gap-4 py-3">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-900">{item.description}</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {item.quantity} × {formatMoney(item.unit_price)}
                      </p>
                    </div>
                    <span className="shrink-0 text-sm font-medium text-slate-900">
                      {formatMoney(item.line_total)}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            <dl className="mt-5 space-y-2 border-t border-slate-200 pt-4 text-sm">
              <div className="flex justify-between">
                <dt className="text-slate-500">Subtotal</dt>
                <dd className="font-medium text-slate-900">{formatMoney(invoice.subtotal)}</dd>
              </div>
              {invoice.discount && (
                <div className="flex justify-between">
                  <dt className="text-slate-500">Discount</dt>
                  <dd className="font-medium text-slate-900">−{formatMoney(invoice.discount)}</dd>
                </div>
              )}
              {invoice.tax && (
                <div className="flex justify-between">
                  <dt className="text-slate-500">Tax</dt>
                  <dd className="font-medium text-slate-900">{formatMoney(invoice.tax)}</dd>
                </div>
              )}
              <div className="flex justify-between border-t border-slate-200 pt-2">
                <dt className="font-semibold text-slate-900">Total</dt>
                <dd className="font-semibold text-slate-900">{formatMoney(invoice.total)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Amount paid</dt>
                <dd className="font-medium text-slate-900">{formatMoney(invoice.amount_paid)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-semibold text-brand-600">Balance due</dt>
                <dd className="font-semibold text-brand-600">{formatMoney(invoice.balance_due)}</dd>
              </div>
            </dl>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Payment history
            </h2>
            {invoice.payments.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">No payments recorded against this invoice yet.</p>
            ) : (
              <ul className="mt-4 divide-y divide-slate-100">
                {invoice.payments.map((payment) => (
                  <li key={payment.id} className="flex items-start justify-between gap-4 py-3">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-900">
                        {formatMoney(payment.amount)}{' '}
                        <span className="font-normal text-slate-500">
                          · {formatEnumLabel(payment.method)}
                        </span>
                      </p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {formatDate(payment.payment_date)}
                        {payment.reference ? ` · Ref ${payment.reference}` : ''}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
            <p className="mt-4 text-xs text-slate-500">
              Payments are recorded by our team when received. To settle a balance, contact us and
              we&apos;ll confirm the details.
            </p>
          </div>
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Issue date</dt>
              <dd className="font-medium text-slate-900">{formatDate(invoice.issue_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Due date</dt>
              <dd className="font-medium text-slate-900">{formatDate(invoice.due_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Project</dt>
              <dd className="font-medium text-slate-900">
                {invoice.project_id ? (
                  <Link
                    to={paths.client.projectDetail(invoice.project_id)}
                    className="text-brand-600 hover:text-brand-700"
                  >
                    View project
                  </Link>
                ) : (
                  'Standalone (no project)'
                )}
              </dd>
            </div>
          </dl>
        </aside>
      </div>
    </div>
  )
}
