import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Globe, SearchX } from 'lucide-react'
import { getClientDomain, type ClientDomainDetail as ClientDomainDetailType } from '@/api/domains'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { domainStatusVariant } from '@/utils/statusBadge'

/**
 * Read-only client view of one of their domains — the click-through target for
 * a DOMAIN_REGISTERED / DOMAIN_STATUS_CHANGED notification. The payload comes
 * from /client/domains/{id}, which has no `notes` field at all, so there is
 * nothing internal to filter out here.
 */
export function ClientDomainDetail() {
  const { domainId } = useParams<{ domainId: string }>()

  const domainQuery = useQuery<ClientDomainDetailType, ApiError>({
    queryKey: ['client', 'domains', 'detail', domainId],
    queryFn: () => getClientDomain(domainId!),
    enabled: Boolean(domainId),
    retry: (count, err) => err.status !== 404 && count < 1,
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
        description="This domain doesn't exist or isn't on your account."
        action={
          <Link
            to={paths.client.domains}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to My Domains
          </Link>
        }
      />
    )
  }

  if (domainQuery.isError || !domainQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this domain"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => domainQuery.refetch()}
      />
    )
  }

  const domain = domainQuery.data

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.client.domains}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Domains
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{domain.domain_name}</h1>
          <Badge variant={domainStatusVariant[domain.status]}>
            {formatEnumLabel(domain.status)}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                <Globe className="size-5" aria-hidden="true" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-slate-900">{domain.domain_name}</h2>
                <p className="text-sm text-slate-500">Registered through {domain.registrar}</p>
              </div>
            </div>
          </div>

          {/* Only meaningful once the domain is pointed somewhere. */}
          {domain.nameservers && (
            <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Nameservers
              </h2>
              <p className="mt-2 text-sm text-slate-500">This domain points at:</p>
              <p className="mt-3 whitespace-pre-line rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 font-mono text-sm text-slate-900">
                {domain.nameservers}
              </p>
            </div>
          )}
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Registrar</dt>
              <dd className="font-medium text-slate-900">{domain.registrar}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Registered</dt>
              <dd className="font-medium text-slate-900">{formatDate(domain.registered_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Expires</dt>
              <dd className="font-medium text-slate-900">{formatDate(domain.expires_at)}</dd>
            </div>
            <div className="border-t border-slate-100 pt-3">
              <dt className="text-slate-500">Total charged</dt>
              <dd className="font-semibold text-brand-600">{formatMoney(domain.total_fee)}</dd>
            </div>
            {domain.hosting_account_id && (
              <div>
                <dt className="text-slate-500">Hosting</dt>
                <dd className="font-medium text-slate-900">
                  <Link
                    to={paths.client.hostingDetail(domain.hosting_account_id)}
                    className="text-brand-600 hover:text-brand-700"
                  >
                    View hosting
                  </Link>
                </dd>
              </div>
            )}
          </dl>

          <p className="border-t border-slate-100 pt-4 text-xs text-slate-500">
            Renewals are handled by our team — we&apos;ll be in touch before this expires.
          </p>
        </aside>
      </div>
    </div>
  )
}
