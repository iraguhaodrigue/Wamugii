import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Calendar, CircleDollarSign, ListChecks, SearchX } from 'lucide-react'
import { getClientProject, listClientMilestones, type ClientProjectDetail as ClientProjectDetailType } from '@/api/clientPortal'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, ProgressBar, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { milestoneStatusVariant, projectPriorityVariant, projectStatusVariant } from '@/utils/statusBadge'

export function ClientProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()

  const projectQuery = useQuery<ClientProjectDetailType, ApiError>({
    queryKey: ['client', 'projects', 'detail', projectId],
    queryFn: () => getClientProject(projectId!),
    enabled: Boolean(projectId),
    retry: (failureCount, err) => err.status !== 404 && failureCount < 1,
  })

  const milestonesQuery = useQuery({
    queryKey: ['client', 'projects', 'milestones', projectId],
    queryFn: () => listClientMilestones(projectId!),
    enabled: Boolean(projectId) && projectQuery.isSuccess,
  })

  if (projectQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-40 rounded-xl" />
      </div>
    )
  }

  const notFound = projectQuery.isError && projectQuery.error.status === 404

  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Project not found"
        description="This project doesn't exist or isn't linked to your account."
        action={
          <Link
            to={paths.client.projects}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to My Projects
          </Link>
        }
      />
    )
  }

  if (projectQuery.isError || !projectQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this project"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => projectQuery.refetch()}
      />
    )
  }

  const project = projectQuery.data
  const milestones = milestonesQuery.data ?? []
  const budget = formatMoney(project.budget)
  const amountPaid = formatMoney(project.amount_paid)

  return (
    <div className="space-y-8">
      <div>
        <Link
          to={paths.client.projects}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Projects
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{project.title}</h1>
          <Badge variant={projectStatusVariant[project.status]}>{formatEnumLabel(project.status)}</Badge>
          <Badge variant={projectPriorityVariant[project.priority]}>{formatEnumLabel(project.priority)} priority</Badge>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Description</h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-600">{project.description}</p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <div className="flex items-center gap-2">
              <ListChecks className="size-4 text-brand-600" aria-hidden="true" />
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Milestones</h2>
            </div>

            <div className="mt-4">
              {milestonesQuery.isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-16 rounded-lg" />
                  ))}
                </div>
              ) : milestonesQuery.isError ? (
                <ErrorState
                  title="Couldn't load milestones"
                  message="Please try again."
                  onRetry={() => milestonesQuery.refetch()}
                  className="py-8"
                />
              ) : milestones.length === 0 ? (
                <p className="py-6 text-center text-sm text-slate-500">No milestones have been added to this project yet.</p>
              ) : (
                <ol className="space-y-4">
                  {milestones.map((milestone, index) => (
                    <li key={milestone.id} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700">
                          {index + 1}
                        </span>
                        {index < milestones.length - 1 && <span className="mt-1 w-px flex-1 bg-slate-200" />}
                      </div>
                      <div className="min-w-0 flex-1 pb-4">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="text-sm font-semibold text-slate-900">{milestone.title}</h3>
                          <Badge variant={milestoneStatusVariant[milestone.status]}>
                            {formatEnumLabel(milestone.status)}
                          </Badge>
                        </div>
                        {milestone.description && <p className="mt-1 text-sm text-slate-500">{milestone.description}</p>}
                        <p className="mt-1.5 text-xs text-slate-400">
                          {milestone.completed_at
                            ? `Completed ${formatDate(milestone.completed_at)}`
                            : milestone.due_date
                              ? `Due ${formatDate(milestone.due_date)}`
                              : 'No due date set'}
                        </p>
                      </div>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-500">Progress</span>
              <span className="font-semibold text-slate-900">{Math.round(project.progress_percentage)}%</span>
            </div>
            <ProgressBar value={project.progress_percentage} className="mt-2" />
          </div>

          <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
            <dl className="space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <dt className="flex items-center gap-1.5 text-slate-500">
                  <CircleDollarSign className="size-4" aria-hidden="true" />
                  Budget
                </dt>
                <dd className="font-medium text-slate-900">{budget ?? 'Not set'}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="flex items-center gap-1.5 text-slate-500">
                  <CircleDollarSign className="size-4" aria-hidden="true" />
                  Amount paid
                </dt>
                <dd className="font-medium text-slate-900">{amountPaid ?? '—'}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="flex items-center gap-1.5 text-slate-500">
                  <Calendar className="size-4" aria-hidden="true" />
                  Start date
                </dt>
                <dd className="font-medium text-slate-900">{formatDate(project.start_date)}</dd>
              </div>
              <div className="flex items-center justify-between gap-3">
                <dt className="flex items-center gap-1.5 text-slate-500">
                  <Calendar className="size-4" aria-hidden="true" />
                  Deadline
                </dt>
                <dd className="font-medium text-slate-900">{formatDate(project.deadline)}</dd>
              </div>
            </dl>
          </div>
        </aside>
      </div>
    </div>
  )
}
