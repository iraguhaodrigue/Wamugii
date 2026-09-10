import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Pencil, Plus, SearchX, Trash2 } from 'lucide-react'
import {
  deactivateInvoice,
  formatRateLabel,
  getInvoice,
  hasVatRate,
  isInvoiceLocked,
  updateInvoice,
  type InvoiceRead,
} from '@/api/invoices'
import { getProject } from '@/api/projects'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import {
  InvoiceForm,
  toIsoDate,
  toItemsPayload,
  toTaxPayload,
  type InvoiceFormValues,
} from '@/components/invoices/InvoiceForm'
import { RecordPaymentModal } from '@/components/invoices/RecordPaymentModal'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { invoiceStatusVariant } from '@/utils/statusBadge'

/** YYYY-MM-DD for `<input type="date">`. */
function toDateInput(value: string | null): string {
  return value ? value.slice(0, 10) : ''
}

export function InvoiceDetail() {
  const { invoiceId } = useParams<{ invoiceId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { usersMap, users } = useUsersMap()

  const [isEditing, setIsEditing] = useState(false)
  const [isPaymentOpen, setIsPaymentOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const invoiceQuery = useQuery<InvoiceRead, ApiError>({
    queryKey: ['invoices', 'detail', invoiceId],
    queryFn: () => getInvoice(invoiceId!),
    enabled: Boolean(invoiceId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  usePageTitle(invoiceQuery.data?.invoice_number ?? 'Invoice')

  const invoice = invoiceQuery.data

  const { data: project } = useQuery({
    queryKey: ['projects', 'detail', invoice?.project_id],
    queryFn: () => getProject(invoice!.project_id!),
    enabled: Boolean(invoice?.project_id),
  })

  const listPath = isAdmin ? paths.admin.invoices : paths.staff.invoices

  const updateMutation = useMutation({
    mutationFn: (values: InvoiceFormValues) => {
      const locked = invoice ? isInvoiceLocked(invoice.status) : false
      // A locked invoice accepts only `notes`; sending anything else returns 409.
      if (locked) {
        return updateInvoice(invoiceId!, { notes: values.notes || null })
      }
      return updateInvoice(invoiceId!, {
        project_id: values.project_id ? Number(values.project_id) : null,
        issue_date: toIsoDate(values.issue_date),
        due_date: toIsoDate(values.due_date),
        ...toTaxPayload(values),
        discount: values.discount || null,
        status: values.status,
        notes: values.notes || null,
        items: toItemsPayload(values),
      })
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(['invoices', 'detail', invoiceId], updated)
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      setIsEditing(false)
      setFormError(null)
    },
    // Surfaces the backend's 409 ("a PAID invoice cannot be edited…") verbatim.
    onError: (err: ApiError) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deactivateInvoice(invoiceId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      navigate(listPath)
    },
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
        description="This invoice doesn't exist."
        action={
          <Link
            to={listPath}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Invoices
          </Link>
        }
      />
    )
  }

  if (invoiceQuery.isError || !invoice) {
    return (
      <ErrorState
        title="Couldn't load this invoice"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => invoiceQuery.refetch()}
      />
    )
  }

  const locked = isInvoiceLocked(invoice.status)
  const client = usersMap.get(invoice.client_id)

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={listPath}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Invoices
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{invoice.invoice_number}</h1>
            <Badge variant={invoiceStatusVariant[invoice.status]}>
              {formatEnumLabel(invoice.status)}
            </Badge>
            {!invoice.is_active && <Badge variant="neutral">Deleted</Badge>}
          </div>
          {!isEditing && (
            <div className="flex items-center gap-2">
              {invoice.status !== 'PAID' && invoice.status !== 'CANCELLED' && (
                <Button
                  size="sm"
                  leftIcon={<Plus className="size-4" />}
                  onClick={() => setIsPaymentOpen(true)}
                >
                  Record Payment
                </Button>
              )}
              <Button
                size="sm"
                variant="outline"
                leftIcon={<Pencil className="size-4" />}
                onClick={() => setIsEditing(true)}
              >
                {locked ? 'Edit note' : 'Edit'}
              </Button>
              {/* Soft delete is ADMIN-only on the backend — hidden for STAFF. */}
              {isAdmin && invoice.is_active && (
                <Button
                  size="sm"
                  variant="danger"
                  leftIcon={<Trash2 className="size-4" />}
                  onClick={() => setIsDeleteOpen(true)}
                >
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
          <InvoiceForm
            mode="edit"
            clients={users}
            notesOnly={locked}
            isSaving={updateMutation.isPending}
            formError={formError}
            defaultValues={{
              client_id: String(invoice.client_id),
              project_id: invoice.project_id ? String(invoice.project_id) : '',
              issue_date: toDateInput(invoice.issue_date),
              due_date: toDateInput(invoice.due_date),
              // Map the derived statuses back onto the settable ones: anything
              // already issued (SENT/PARTIALLY_PAID/OVERDUE/PAID) is "SENT", so
              // saving an OVERDUE invoice doesn't silently demote it to DRAFT.
              status:
                invoice.status === 'CANCELLED'
                  ? 'CANCELLED'
                  : invoice.status === 'DRAFT'
                    ? 'DRAFT'
                    : 'SENT',
              vat_enabled: hasVatRate(invoice.tax_rate),
              tax: invoice.tax ?? '',
              discount: invoice.discount ?? '',
              notes: invoice.notes ?? '',
              items: invoice.items.map((item) => ({
                description: item.description,
                quantity: item.quantity,
                unit_price: item.unit_price,
              })),
            }}
            onSubmit={(values) => updateMutation.mutate(values)}
            onCancel={() => {
              setIsEditing(false)
              setFormError(null)
            }}
          />
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Line items</h2>
              {invoice.items.length === 0 ? (
                <p className="mt-4 text-sm text-slate-500">
                  No line items on this invoice — the total was entered directly.
                </p>
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
                {invoice.tax && (
                  <div className="flex justify-between">
                    <dt className="text-slate-500">
                      {hasVatRate(invoice.tax_rate)
                        ? `VAT (${formatRateLabel(invoice.tax_rate!)}%)`
                        : 'Tax'}
                    </dt>
                    <dd className="font-medium text-slate-900">{formatMoney(invoice.tax)}</dd>
                  </div>
                )}
                {invoice.discount && (
                  <div className="flex justify-between">
                    <dt className="text-slate-500">Discount</dt>
                    <dd className="font-medium text-slate-900">−{formatMoney(invoice.discount)}</dd>
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
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Payments</h2>
                <span className="text-xs text-slate-500">Manually recorded — no online payment</span>
              </div>
              {invoice.payments.length === 0 ? (
                <p className="mt-4 text-sm text-slate-500">No payments recorded yet.</p>
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
                        {payment.notes && (
                          <p className="mt-1 text-xs text-slate-500">{payment.notes}</p>
                        )}
                      </div>
                      <span className="shrink-0 text-xs text-slate-500">
                        by {usersMap.get(payment.recorded_by)?.full_name ?? `#${payment.recorded_by}`}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Client</dt>
                <dd className="font-medium text-slate-900">
                  {client ? client.full_name : `#${invoice.client_id}`}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Project</dt>
                <dd className="font-medium text-slate-900">
                  {invoice.project_id ? (
                    <Link
                      to={
                        isAdmin
                          ? paths.admin.projectDetail(invoice.project_id)
                          : paths.staff.projectDetail(invoice.project_id)
                      }
                      className="text-brand-600 hover:text-brand-700"
                    >
                      {project?.title ?? `#${invoice.project_id}`}
                    </Link>
                  ) : (
                    'Standalone (no project)'
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Issue date</dt>
                <dd className="font-medium text-slate-900">{formatDate(invoice.issue_date)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Due date</dt>
                <dd className="font-medium text-slate-900">{formatDate(invoice.due_date)}</dd>
              </div>
            </dl>

            {invoice.notes && (
              <div className="border-t border-slate-100 pt-4">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                  Internal notes
                </h3>
                <p className="mt-2 whitespace-pre-line text-sm text-slate-600">{invoice.notes}</p>
                <p className="mt-2 text-xs text-slate-500">Never shown to the client.</p>
              </div>
            )}
          </aside>
        </div>
      )}

      <RecordPaymentModal
        isOpen={isPaymentOpen}
        onClose={() => setIsPaymentOpen(false)}
        invoiceId={invoice.id}
        balanceDue={invoice.balance_due}
        onRecorded={() => {
          setIsPaymentOpen(false)
          // Refetch so the new balance and derived status appear immediately.
          invoiceQuery.refetch()
          queryClient.invalidateQueries({ queryKey: ['invoices'] })
          queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
        }}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this invoice?"
        description="This deactivates the invoice. It will no longer appear in the list or for the client."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
