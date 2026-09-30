import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, SearchX, Server } from 'lucide-react'
import { getClientHosting, type ClientHostingDetail as ClientHostingDetailType } from '@/api/hosting'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { hostingStatusVariant } from '@/utils/statusBadge'

/**
 * Read-only client view. The payload comes from /client/hosting/{id}, which the
 * backend scopes to the signed-in client and which has no `server_notes` field
 * at all — there is nothing to filter out here.
 */
export function ClientHostingDetail() {
  const { accountId } = useParams<{ accountId: string }>()

  const accountQuery = useQuery<ClientHostingDetailType, ApiError>({
    queryKey: ['client', 'hosting', 'detail', accountId],
    queryFn: () => getClientHosting(accountId!),
    enabled: Boolean(accountId),
    retry: (count, err) => err.status !== 404 && count < 1,
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
        title="Hosting not found"
        description="This hosting account doesn't exist or isn't linked to your account."
        action={
          <Link
            to={paths.client.hosting}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to My Hosting
          </Link>
        }
      />
    )
  }

  if (accountQuery.isError || !accountQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this hosting account"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => accountQuery.refetch()}
      />
    )
  }

  const account = accountQuery.data
  const plan = account.plan
  const features = (plan?.features ?? '')
    .split(',')
    .map((f) => f.trim())
    .filter(Boolean)

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.client.hosting}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Hosting
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            {account.domain ?? `Hosting #${account.id}`}
          </h1>
          <Badge variant={hostingStatusVariant[account.status]}>
            {formatEnumLabel(account.status)}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <Server className="size-5" aria-hidden="true" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-slate-900">{plan?.name ?? 'Hosting'}</h2>
                {plan?.description && (
                  <p className="text-sm text-slate-500">{plan.description}</p>
                )}
              </div>
            </div>

            {features.length > 0 && (
              <ul className="mt-5 space-y-2">
                {features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-sm text-slate-600">
                    <Check className="mt-0.5 size-4 shrink-0 text-brand-400" aria-hidden="true" />
                    {feature}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Only meaningful once we've set the account up. */}
          {account.nameservers && (
            <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Nameservers
              </h2>
              <p className="mt-2 text-sm text-slate-500">
                Point your domain&apos;s DNS at these:
              </p>
              <p className="mt-3 whitespace-pre-line rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-sm text-slate-900">
                {account.nameservers}
              </p>
              <p className="mt-3 text-xs text-slate-500">
                Not sure how? Get in touch and we&apos;ll walk you through it.
              </p>
            </div>
          )}
        </div>

        <aside className="space-y-4">
          <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Domain</dt>
                <dd className="font-medium text-slate-900">{account.domain ?? 'Not set yet'}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Billing cycle</dt>
                <dd className="font-medium text-slate-900">
                  {formatEnumLabel(account.billing_cycle)}
                  {plan && (
                    <span className="font-normal text-slate-500">
                      {' · '}
                      {formatMoney(
                        account.billing_cycle === 'YEARLY' ? plan.yearly_price : plan.monthly_price,
                      )}
                    </span>
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Started</dt>
                <dd className="font-medium text-slate-900">{formatDate(account.start_date)}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Next billing</dt>
                <dd className="font-medium text-slate-900">
                  {formatDate(account.next_billing_date)}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Expires</dt>
                <dd className="font-medium text-slate-900">{formatDate(account.expires_at)}</dd>
              </div>
            </dl>
          </div>

          <Link
            to={`${paths.requestQuote}?service=hosting`}
            className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
          >
            Renew / Upgrade
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </aside>
      </div>
    </div>
  )
}
