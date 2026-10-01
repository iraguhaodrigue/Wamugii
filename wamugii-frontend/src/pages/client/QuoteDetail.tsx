import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, FileText, SearchX } from 'lucide-react'
import { getClientQuote, type ClientQuoteDetail as ClientQuoteDetailType } from '@/api/clientPortal'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDateTime, formatEnumLabel } from '@/utils/format'
import { quoteStatusVariant } from '@/utils/statusBadge'

/**
 * Read-only client view of one of their own quote requests — the click-through
 * target for a QUOTE_STATUS_CHANGED notification. The payload comes from
 * /client/quotes/{id}, which carries no `admin_notes`, so there is nothing
 * internal to filter out here.
 */
export function ClientQuoteDetail() {
  const { quoteId } = useParams<{ quoteId: string }>()

  const quoteQuery = useQuery<ClientQuoteDetailType, ApiError>({
    queryKey: ['client', 'quotes', 'detail', quoteId],
    queryFn: () => getClientQuote(quoteId!),
    enabled: Boolean(quoteId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  if (quoteQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = quoteQuery.isError && quoteQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Quote request not found"
        description="This request doesn't exist or wasn't submitted with your email address."
        action={
          <Link
            to={paths.client.dashboard}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Dashboard
          </Link>
        }
      />
    )
  }

  if (quoteQuery.isError || !quoteQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this quote request"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => quoteQuery.refetch()}
      />
    )
  }

  const quote = quoteQuery.data

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.client.dashboard}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Dashboard
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            {quote.project_title}
          </h1>
          <Badge variant={quoteStatusVariant[quote.status]}>{formatEnumLabel(quote.status)}</Badge>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Quote request #{quote.id} · submitted {formatDateTime(quote.created_at)}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <FileText className="size-4" aria-hidden="true" />
              What you asked for
            </h2>
            <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-slate-700">
              {quote.project_description}
            </p>
          </div>

          {quote.converted_project_id && (
            <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                This request is underway
              </h2>
              <p className="mt-2 text-sm text-slate-500">
                We turned this into a project — track progress and milestones there.
              </p>
              <Link
                to={paths.client.projectDetail(quote.converted_project_id)}
                className="mt-4 inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
              >
                View project
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
          )}
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Service</dt>
              <dd className="font-medium text-slate-900">
                {quote.service_name ??
                  (quote.service_id ? `Service #${quote.service_id}` : 'General enquiry')}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Budget range</dt>
              <dd className="font-medium text-slate-900">{quote.budget_range ?? 'Not specified'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Preferred deadline</dt>
              {/* Free text on the quote form ("in 2 months"), not a date. */}
              <dd className="font-medium text-slate-900">
                {quote.preferred_deadline ?? 'Not specified'}
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Last update</dt>
              <dd className="font-medium text-slate-900">{formatDateTime(quote.updated_at)}</dd>
            </div>
          </dl>

          <p className="border-t border-slate-100 pt-4 text-xs text-slate-500">
            Questions about this quote? Open a{' '}
            <Link to={paths.client.tickets} className="text-brand-600 hover:text-brand-700">
              support ticket
            </Link>{' '}
            and we&apos;ll pick it up.
          </p>
        </aside>
      </div>
    </div>
  )
}
