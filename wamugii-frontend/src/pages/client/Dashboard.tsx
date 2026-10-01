import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Activity, ArrowRight, CheckCircle2, Clock, FolderKanban, TrendingUp } from 'lucide-react'
import { getClientDashboard } from '@/api/clientPortal'
import { listClientHosting } from '@/api/hosting'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton, StatCard } from '@/components/ui'
import { ClientProjectRow } from '@/components/projects/ClientProjectRow'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { hostingStatusVariant, quoteStatusVariant } from '@/utils/statusBadge'

export function ClientDashboard() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['client', 'dashboard'],
    queryFn: getClientDashboard,
  })

  // Separate from the dashboard payload so the existing endpoint's shape stays
  // untouched; the summary simply doesn't render if this is empty or fails.
  const hostingQuery = useQuery({ queryKey: ['client', 'hosting'], queryFn: listClientHosting })
  const hostingAccounts = hostingQuery.data ?? []

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Couldn't load your dashboard"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => refetch()}
      />
    )
  }

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          Welcome back, {data.user.full_name.split(' ')[0]}
        </h1>
        <p className="mt-1 text-sm text-slate-500">Here&apos;s what&apos;s happening across your projects.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={FolderKanban} label="Total Projects" value={data.summary.total_projects} accent="brand" />
        <StatCard icon={TrendingUp} label="Active Projects" value={data.summary.active_projects} accent="accent" />
        <StatCard icon={CheckCircle2} label="Completed Projects" value={data.summary.completed_projects} accent="success" />
        <StatCard icon={Clock} label="Pending Quotes" value={data.summary.pending_quotes} accent="warning" />
      </div>

      {/* Only rendered when the client actually has hosting — no empty tile. */}
      {hostingAccounts.length > 0 && (
        <section>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">My Hosting</h2>
            <Link
              to={paths.client.hosting}
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              View all
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {hostingAccounts.slice(0, 2).map((account) => (
              <Link
                key={account.id}
                to={paths.client.hostingDetail(account.id)}
                className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-panel p-4 shadow-[var(--shadow-card)] backdrop-blur-sm transition-colors hover:border-brand-400/30"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900">
                    {account.domain ?? `Hosting #${account.id}`}
                  </p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {account.plan?.name ?? 'Hosting'}
                    {account.next_billing_date
                      ? ` · renews ${formatDate(account.next_billing_date)}`
                      : ''}
                  </p>
                </div>
                <Badge variant={hostingStatusVariant[account.status]}>
                  {formatEnumLabel(account.status)}
                </Badge>
              </Link>
            ))}
          </div>
        </section>
      )}

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Recent Projects</h2>
          <Link
            to={paths.client.projects}
            className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
          >
            View all
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </div>
        <div className="mt-4 space-y-3">
          {data.recent_projects.length === 0 ? (
            <EmptyState
              icon={FolderKanban}
              title="No projects yet"
              description="Once you have an active project, it'll show up here."
            />
          ) : (
            data.recent_projects.map((project) => <ClientProjectRow key={project.id} project={project} />)
          )}
        </div>
      </section>

      <div className="grid gap-8 lg:grid-cols-2">
        <section>
          <h2 className="text-lg font-semibold text-slate-900">Recent Quotes</h2>
          <div className="mt-4 space-y-3">
            {data.recent_quotes.length === 0 ? (
              <EmptyState title="No quote requests yet" description="Submit a request and it'll appear here." />
            ) : (
              data.recent_quotes.map((quote) => (
                <Link
                  key={quote.id}
                  to={paths.client.quoteDetail(quote.id)}
                  className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-panel p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">{quote.project_title}</p>
                    <p className="mt-0.5 text-xs text-slate-500">Submitted {formatDate(quote.created_at)}</p>
                  </div>
                  <Badge variant={quoteStatusVariant[quote.status]}>{formatEnumLabel(quote.status)}</Badge>
                </Link>
              ))
            )}
          </div>
        </section>

        <section>
          <h2 className="text-lg font-semibold text-slate-900">Recent Activity</h2>
          <div className="mt-4 rounded-xl border border-slate-200 bg-panel p-4 shadow-sm">
            {data.recent_activity.length === 0 ? (
              <p className="py-6 text-center text-sm text-slate-500">No recent activity.</p>
            ) : (
              <ul className="space-y-4">
                {data.recent_activity.map((item, index) => (
                  <li key={index} className="flex gap-3">
                    <div className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-600">
                      <Activity className="size-3.5" aria-hidden="true" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-slate-700">{item.message}</p>
                      <p className="text-xs text-slate-400">{formatDate(item.created_at)}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
