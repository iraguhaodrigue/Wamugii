import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2, FolderKanban, Sparkles } from 'lucide-react'
import { listMyProjects } from '@/api/team'
import { useAuth } from '@/context/AuthContext'
import { paths } from '@/routes/paths'
import { Avatar, Badge, EmptyState, ErrorState, Skeleton, StatCard } from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { projectPriorityVariant, projectRoleVariant, projectStatusVariant } from '@/utils/statusBadge'

const ACTIVE_STATUSES = ['PLANNING', 'IN_PROGRESS', 'TESTING', 'CLIENT_REVIEW']

/**
 * The team member's landing page.
 *
 * Everything shown here comes from /team/projects, which carries no client or
 * billing field at all — so there is nothing on this page that could leak one.
 */
export function TeamDashboard() {
  const { user } = useAuth()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['team', 'projects'],
    queryFn: listMyProjects,
  })

  if (isLoading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-32 rounded-xl" />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Couldn't load your projects"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => refetch()}
      />
    )
  }

  const active = data.filter((p) => ACTIVE_STATUSES.includes(p.status))
  const completed = data.filter((p) => p.status === 'COMPLETED')
  const leading = data.filter((p) => p.my_role === 'TEAM_LEAD')

  return (
    <div className="space-y-8">
      <div className="relative overflow-hidden rounded-xl bg-brand-700 p-6 shadow-lg shadow-brand-950/30 sm:p-8">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.15]"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }}
          aria-hidden="true"
        />
        <div className="relative flex items-center gap-4">
          {user && <Avatar name={user.full_name} size="lg" className="ring-2 ring-white/30" />}
          <div>
            <p className="flex items-center gap-1.5 text-sm font-medium text-brand-100">
              <Sparkles className="size-4" aria-hidden="true" />
              Welcome back
            </p>
            <h2 className="mt-0.5 text-2xl font-bold text-white">
              {user?.full_name.split(' ')[0]}
            </h2>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard icon={FolderKanban} label="Assigned Projects" value={data.length} accent="brand" />
        <StatCard icon={Sparkles} label="In Flight" value={active.length} accent="accent" />
        <StatCard
          icon={CheckCircle2}
          label="Completed"
          value={completed.length}
          accent="success"
        />
      </div>

      {leading.length > 0 && (
        <p className="text-sm text-slate-500">
          You&apos;re the team lead on{' '}
          <span className="font-semibold text-slate-700">
            {leading.length === 1 ? leading[0]?.title : `${leading.length} projects`}
          </span>
          .
        </p>
      )}

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">My Projects</h2>
          {data.length > 0 && (
            <Link
              to={paths.team.projects}
              className="inline-flex items-center gap-1 text-sm font-medium text-brand-600 hover:text-brand-700"
            >
              View all
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          )}
        </div>

        <div className="mt-4 space-y-3">
          {data.length === 0 ? (
            <EmptyState
              icon={FolderKanban}
              title="No projects yet"
              description="Once you're assigned to a project it'll show up here, and we'll email you."
            />
          ) : (
            data.slice(0, 5).map((project) => (
              <Link
                key={project.id}
                to={paths.team.projectDetail(project.id)}
                className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-panel p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-slate-900">{project.title}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {project.deadline ? `Deadline ${formatDate(project.deadline)}` : 'No deadline set'}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <Badge variant={projectRoleVariant[project.my_role]}>
                    {formatEnumLabel(project.my_role)}
                  </Badge>
                  <Badge variant={projectStatusVariant[project.status]}>
                    {formatEnumLabel(project.status)}
                  </Badge>
                  <Badge variant={projectPriorityVariant[project.priority]}>
                    {formatEnumLabel(project.priority)}
                  </Badge>
                </div>
              </Link>
            ))
          )}
        </div>
      </section>
    </div>
  )
}
