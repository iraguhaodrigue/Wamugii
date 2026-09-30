import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Receipt, SearchX, Trash2 } from 'lucide-react'
import {
  DISRUPTIVE_STATUSES,
  SETTABLE_HOSTING_STATUSES,
  deactivateHostingAccount,
  getHostingAccount,
  priceForCycle,
  updateHostingAccount,
  type HostingAccount,
  type HostingStatus,
} from '@/api/hosting'
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
import { hostingStatusVariant } from '@/utils/statusBadge'

export function HostingAccountDetail() {
  const { accountId } = useParams<{ accountId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { usersMap, users } = useUsersMap()

  const [pendingStatus, setPendingStatus] = useState<HostingStatus | null>(null)
  const [notesDraft, setNotesDraft] = useState<string | null>(null)
  const [nameserversDraft, setNameserversDraft] = useState<string | null>(null)
  const [isInvoiceOpen, setIsInvoiceOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const accountQuery = useQuery<HostingAccount, ApiError>({
    queryKey: ['hosting', 'accounts', 'detail', accountId],
    queryFn: () => getHostingAccount(accountId!),
    enabled: Boolean(accountId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const account = accountQuery.data
  usePageTitle(account?.domain ?? 'Hosting Account')

  const listPath = isAdmin ? paths.admin.hostingAccounts : paths.staff.hostingAccounts

  const updateMutation = useMutation({
    mutationFn: (payload: Parameters<typeof updateHostingAccount>[1]) =>
      updateHostingAccount(accountId!, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['hosting', 'accounts', 'detail', accountId], updated)
      queryClient.invalidateQueries({ queryKey: ['hosting'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      setPendingStatus(null)
      setNotesDraft(null)
      setNameserversDraft(null)
      setFormError(null)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deactivateHostingAccount(accountId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosting'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      navigate(listPath)
    },
  })

  if (accountQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = accountQuery.isError && accountQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Hosting account not found"
        description="This hosting account doesn't exist."
        action={
          <Link
            to={listPath}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Hosting
          </Link>
        }
      />
    )
  }

  if (accountQuery.isError || !account) {
    return (
      <ErrorState
        title="Couldn't load this hosting account"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => accountQuery.refetch()}
      />
    )
  }

  const client = usersMap.get(account.client_id)
  const plan = account.plan
  const cyclePrice = plan ? priceForCycle(plan, account.billing_cycle) : null

  function applyStatus(next: HostingStatus) {
    // Suspending or cancelling emails the client, so confirm first.
    if (DISRUPTIVE_STATUSES.includes(next)) {
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
          Back to Hosting
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              {account.domain ?? `Hosting #${account.id}`}
            </h1>
            <Badge variant={hostingStatusVariant[account.status]}>
              {formatEnumLabel(account.status)}
            </Badge>
            {!account.is_active && <Badge variant="neutral">Deleted</Badge>}
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              leftIcon={<Receipt className="size-4" />}
              onClick={() => setIsInvoiceOpen(true)}
            >
              Generate Invoice
            </Button>
            {isAdmin && account.is_active && (
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
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Setup
            </h2>

            <div className="mt-4 space-y-4">
              <Select
                label="Status"
                options={SETTABLE_HOSTING_STATUSES.map((s) => ({
                  value: s,
                  label: formatEnumLabel(s),
                }))}
                value={account.status}
                disabled={updateMutation.isPending}
                onChange={(e) => applyStatus(e.target.value as HostingStatus)}
                hint="Marking this Active emails the client with the nameservers below."
              />

              <div className="space-y-2">
                <Textarea
                  label="Nameservers"
                  rows={2}
                  hint="What the client points their DNS to — filled in after server setup"
                  value={nameserversDraft ?? account.nameservers ?? ''}
                  onChange={(e) => setNameserversDraft(e.target.value)}
                />
                {nameserversDraft !== null && nameserversDraft !== (account.nameservers ?? '') && (
                  <div className="flex justify-end gap-2">
                    <Button size="sm" variant="outline" onClick={() => setNameserversDraft(null)}>
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      isLoading={updateMutation.isPending}
                      onClick={() =>
                        updateMutation.mutate({ nameservers: nameserversDraft || null })
                      }
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
              Which droplet, control-panel user, and so on. Never shown to the client.
            </p>
            <div className="mt-4 space-y-2">
              <Textarea
                label="Server notes"
                rows={4}
                value={notesDraft ?? account.server_notes ?? ''}
                onChange={(e) => setNotesDraft(e.target.value)}
              />
              {notesDraft !== null && notesDraft !== (account.server_notes ?? '') && (
                <div className="flex justify-end gap-2">
                  <Button size="sm" variant="outline" onClick={() => setNotesDraft(null)}>
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    isLoading={updateMutation.isPending}
                    onClick={() => updateMutation.mutate({ server_notes: notesDraft || null })}
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
                {client ? (
                  <Link
                    to={paths.admin.userDetail(account.client_id)}
                    className="text-brand-600 hover:text-brand-700"
                  >
                    {client.full_name}
                  </Link>
                ) : (
                  `#${account.client_id}`
                )}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Plan</dt>
              <dd className="font-medium text-slate-900">{plan?.name ?? `#${account.plan_id}`}</dd>
            </div>
            {plan && (
              <div>
                <dt className="text-slate-500">Includes</dt>
                <dd className="text-slate-600">{plan.features}</dd>
              </div>
            )}
            <div>
              <dt className="text-slate-500">Billing cycle</dt>
              <dd className="font-medium text-slate-900">
                {formatEnumLabel(account.billing_cycle)}
                {cyclePrice && (
                  <span className="font-normal text-slate-500"> · {formatMoney(cyclePrice)}</span>
                )}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Start date</dt>
              <dd className="font-medium text-slate-900">{formatDate(account.start_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Next billing</dt>
              <dd className="font-medium text-slate-900">{formatDate(account.next_billing_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Expires</dt>
              <dd className="font-medium text-slate-900">{formatDate(account.expires_at)}</dd>
            </div>
            {account.invoice_id && (
              <div>
                <dt className="text-slate-500">Latest invoice</dt>
                <dd className="font-medium text-slate-900">
                  <Link
                    to={
                      isAdmin
                        ? paths.admin.invoiceDetail(account.invoice_id)
                        : paths.staff.invoiceDetail(account.invoice_id)
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

      {/* Reuses the existing invoice flow, prefilled with this client and a
          line item for the plan at the price for its billing cycle. */}
      <CreateInvoiceModal
        key={isInvoiceOpen ? 'invoice-open' : 'invoice-closed'}
        isOpen={isInvoiceOpen}
        onClose={() => setIsInvoiceOpen(false)}
        clients={users}
        defaultValues={{
          client_id: String(account.client_id),
          status: 'SENT',
          items: [
            {
              description: plan
                ? `${plan.name} hosting — ${formatEnumLabel(account.billing_cycle)}${
                    account.domain ? ` (${account.domain})` : ''
                  }`
                : 'Hosting',
              quantity: '1',
              unit_price: cyclePrice ?? '0',
            },
          ],
        }}
        onCreated={(invoice) => {
          setIsInvoiceOpen(false)
          // Point the account at the invoice just raised for it.
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
        title={pendingStatus === 'CANCELLED' ? 'Cancel this hosting?' : 'Suspend this hosting?'}
        description={
          pendingStatus === 'CANCELLED'
            ? 'The client will be emailed that their hosting has been cancelled.'
            : 'The client will be emailed that their hosting has been suspended.'
        }
        confirmLabel={pendingStatus === 'CANCELLED' ? 'Cancel hosting' : 'Suspend'}
        isDanger
        isLoading={updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this hosting account?"
        description="This deactivates the record. It will no longer appear in the list or for the client."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
