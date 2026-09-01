import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, FolderKanban, MessageSquare } from 'lucide-react'
import { listProjects } from '@/api/projects'
import { listQuoteRequests } from '@/api/quoteRequests'
import { useUsersMap } from '@/hooks/useUsersMap'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { projectStatusVariant, quoteStatusVariant } from '@/utils/statusBadge'

export function StaffOverview() {
  usePageTitle('Overview')
  const { usersMap } = useUsersMap()

  const projectsQuery = useQuery({
    queryKey: ['projects', 'overview'],
    queryFn: () => listProjects({ limit: 5 }),
  })

  const quotesQuery = useQuery({
    queryKey: ['quote-requests', 'overview'],
    queryFn: () => listQuoteRequests({ limit: 5 }),
  })

  return (
    <div className="space-y-8">
      <p className="text-sm text-slate-500">A quick look at what's most recent. Use Projects or Quote Requests for the full picture.</p>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <FolderKanban className="size-4" aria-hidden="true" />
              Recent Projects
            </h2>
            <Link to={paths.staff.projects} className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700">
              View all
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {projectsQuery.isLoading ? (
              Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)
            ) : projectsQuery.isError ? (
              <ErrorState title="Couldn't load projects" onRetry={() => projectsQuery.refetch()} className="py-8" />
            ) : projectsQuery.data && projectsQuery.data.length > 0 ? (
              projectsQuery.data.map((project) => (
                <Link
                  key={project.id}
                  to={paths.staff.projectDetail(project.id)}
                  className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3 transition-colors hover:border-brand-200 hover:bg-brand-600/10"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">{project.title}</p>
                    <p className="text-xs text-slate-500">
                      {usersMap.get(project.client_id)?.full_name ?? `Client #${project.client_id}`} · {formatDate(project.created_at)}
                    </p>
                  </div>
                  <Badge variant={projectStatusVariant[project.status]}>{formatEnumLabel(project.status)}</Badge>
                </Link>
              ))
            ) : (
              <EmptyState title="No projects yet" className="py-8" />
            )}
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <MessageSquare className="size-4" aria-hidden="true" />
              Recent Quote Requests
            </h2>
            <Link to={paths.staff.quotes} className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700">
              View all
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>

          <div className="mt-4 space-y-3">
            {quotesQuery.isLoading ? (
              Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-14 rounded-lg" />)
            ) : quotesQuery.isError ? (
              <ErrorState title="Couldn't load quotes" onRetry={() => quotesQuery.refetch()} className="py-8" />
            ) : quotesQuery.data && quotesQuery.data.length > 0 ? (
              quotesQuery.data.map((quote) => (
                <Link
                  key={quote.id}
                  to={paths.staff.quoteDetail(quote.id)}
                  className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3 transition-colors hover:border-brand-200 hover:bg-brand-600/10"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">{quote.project_title}</p>
                    <p className="text-xs text-slate-500">
                      {quote.full_name} · {formatDate(quote.created_at)}
                    </p>
                  </div>
                  <Badge variant={quoteStatusVariant[quote.status]}>{formatEnumLabel(quote.status)}</Badge>
                </Link>
              ))
            ) : (
              <EmptyState title="No quote requests yet" className="py-8" />
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
