import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Receipt, SearchX, Trash2 } from 'lucide-react'
import {
  DISRUPTIVE_DOMAIN_STATUSES,
  SETTABLE_DOMAIN_STATUSES,
  deactivateDomain,
  getDomain,
  updateDomain,
  type Domain,
  type DomainStatus,
} from '@/api/domains'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  Select,
  Skeleton,
  Textarea,
} from '@/components/ui'
import { CreateInvoiceModal } from '@/components/invoices/CreateInvoiceModal'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { domainStatusVariant } from '@/utils/statusBadge'

export function DomainDetail() {
  const { domainId } = useParams<{ domainId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { usersMap, users } = useUsersMap()

  const [pendingStatus, setPendingStatus] = useState<DomainStatus | null>(null)
  const [nameserversDraft, setNameserversDraft] = useState<string | null>(null)
  const [notesDraft, setNotesDraft] = useState<string | null>(null)
  const [isInvoiceOpen, setIsInvoiceOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const domainQuery = useQuery<Domain, ApiError>({
    queryKey: ['domains', 'detail', domainId],
    queryFn: () => getDomain(domainId!),
    enabled: Boolean(domainId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const domain = domainQuery.data
  usePageTitle(domain?.domain_name ?? 'Domain')

  const listPath = isAdmin ? paths.admin.domains : paths.staff.domains

  const updateMutation = useMutation({
    mutationFn: (payload: Parameters<typeof updateDomain>[1]) => updateDomain(domainId!, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['domains', 'detail', domainId], updated)
      queryClient.invalidateQueries({ queryKey: ['domains'] })
      setPendingStatus(null)
      setNameserversDraft(null)
      setNotesDraft(null)
      setFormError(null)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deactivateDomain(domainId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
      navigate(listPath)
    },
  })

  if (domainQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = domainQuery.isError && domainQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Domain not found"
        description="This domain record doesn't exist."
        action={
          <Link
            to={listPath}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Domains
          </Link>
        }
      />
    )
  }

  if (domainQuery.isError || !domain) {
    return (
      <ErrorState
        title="Couldn't load this domain"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => domainQuery.refetch()}
      />
    )
  }

  const client = usersMap.get(domain.client_id)

  function applyStatus(next: DomainStatus) {
    // Cancelling emails the client, so confirm first.
    if (DISRUPTIVE_DOMAIN_STATUSES.includes(next)) {
      setPendingStatus(next)
      return
    }
    updateMutation.mutate({ status: next })
  }

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={listPath}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Domains
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              {domain.domain_name}
            </h1>
            <Badge variant={domainStatusVariant[domain.status]}>
              {formatEnumLabel(domain.status)}
            </Badge>
            {!domain.is_active && <Badge variant="neutral">Deleted</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              leftIcon={<Receipt className="size-4" />}
              onClick={() => setIsInvoiceOpen(true)}
            >
              Generate Invoice
            </Button>
            {isAdmin && domain.is_active && (
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
        </div>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Setup</h2>
            <div className="mt-4 space-y-4">
              <Select
                label="Status"
                options={SETTABLE_DOMAIN_STATUSES.map((s) => ({
                  value: s,
                  label: formatEnumLabel(s),
                }))}
                value={domain.status}
                disabled={updateMutation.isPending}
                onChange={(e) => applyStatus(e.target.value as DomainStatus)}
                hint="Marking this Active emails the client with the nameservers below."
              />

              <div className="space-y-2">
                <Textarea
                  label="Nameservers"
                  rows={2}
                  hint="What the domain points at — filled in after registration"
                  value={nameserversDraft ?? domain.nameservers ?? ''}
                  onChange={(e) => setNameserversDraft(e.target.value)}
                />
                {nameserversDraft !== null && nameserversDraft !== (domain.nameservers ?? '') && (
                  <div className="flex justify-end gap-2">
                    <Button size="sm" variant="outline" onClick={() => setNameserversDraft(null)}>
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      isLoading={updateMutation.isPending}
                      onClick={() => updateMutation.mutate({ nameservers: nameserversDraft || null })}
                    >
                      Save Nameservers
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Internal notes
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Reseller account, margin, renewal reminders. Never shown to the client.
            </p>
            <div className="mt-4 space-y-2">
              <Textarea
                label="Notes"
                rows={4}
                value={notesDraft ?? domain.notes ?? ''}
                onChange={(e) => setNotesDraft(e.target.value)}
              />
              {notesDraft !== null && notesDraft !== (domain.notes ?? '') && (
                <div className="flex justify-end gap-2">
                  <Button size="sm" variant="outline" onClick={() => setNotesDraft(null)}>
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    isLoading={updateMutation.isPending}
                    onClick={() => updateMutation.mutate({ notes: notesDraft || null })}
                  >
                    Save Notes
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Client</dt>
              <dd className="font-medium text-slate-900">
                {client ? client.full_name : `#${domain.client_id}`}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Registrar</dt>
              <dd className="font-medium text-slate-900">{domain.registrar}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Registration fee</dt>
              <dd className="font-medium text-slate-900">{formatMoney(domain.registration_fee)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Service fee</dt>
              <dd className="font-medium text-slate-900">
                {domain.service_fee ? formatMoney(domain.service_fee) : '—'}
              </dd>
            </div>
            <div className="border-t border-slate-100 pt-3">
              <dt className="text-slate-500">Total</dt>
              <dd className="font-semibold text-brand-600">{formatMoney(domain.total_fee)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Registered</dt>
              <dd className="font-medium text-slate-900">{formatDate(domain.registered_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Expires</dt>
              <dd className="font-medium text-slate-900">{formatDate(domain.expires_at)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Hosting</dt>
              <dd className="font-medium text-slate-900">
                {domain.hosting_account_id ? (
                  <Link
                    to={
                      isAdmin
                        ? paths.admin.hostingAccountDetail(domain.hosting_account_id)
                        : paths.staff.hostingAccountDetail(domain.hosting_account_id)
                    }
                    className="text-brand-600 hover:text-brand-700"
                  >
                    View hosting
                  </Link>
                ) : (
                  'Not linked'
                )}
              </dd>
            </div>
            {domain.invoice_id && (
              <div>
                <dt className="text-slate-500">Invoice</dt>
                <dd className="font-medium text-slate-900">
                  <Link
                    to={
                      isAdmin
                        ? paths.admin.invoiceDetail(domain.invoice_id)
                        : paths.staff.invoiceDetail(domain.invoice_id)
                    }
                    className="text-brand-600 hover:text-brand-700"
                  >
                    View invoice
                  </Link>
                </dd>
              </div>
            )}
          </dl>
        </aside>
      </div>

      {/* Reuses the existing invoice flow, prefilled with one line item for the
          registration + service fee. */}
      <CreateInvoiceModal
        key={isInvoiceOpen ? 'invoice-open' : 'invoice-closed'}
        isOpen={isInvoiceOpen}
        onClose={() => setIsInvoiceOpen(false)}
        clients={users}
        defaultValues={{
          client_id: String(domain.client_id),
          status: 'SENT',
          items: [
            {
              description: `Domain ${domain.domain_name} — registration + service (${domain.registrar})`,
              quantity: '1',
              unit_price: domain.total_fee,
            },
          ],
        }}
        onCreated={(invoice) => {
          setIsInvoiceOpen(false)
          updateMutation.mutate({ invoice_id: invoice.id })
          navigate(
            isAdmin ? paths.admin.invoiceDetail(invoice.id) : paths.staff.invoiceDetail(invoice.id),
          )
        }}
      />

      <ConfirmDialog
        isOpen={pendingStatus !== null}
        onClose={() => setPendingStatus(null)}
        onConfirm={() => pendingStatus && updateMutation.mutate({ status: pendingStatus })}
        title="Cancel this domain?"
        description="The client will be emailed that their domain registration has been cancelled."
        confirmLabel="Cancel domain"
        isDanger
        isLoading={updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this domain record?"
        description="This deactivates the record. It will no longer appear in the list or for the client."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
