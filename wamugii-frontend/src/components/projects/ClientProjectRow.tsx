import { Link } from 'react-router-dom'
import { Calendar } from 'lucide-react'
import type { ClientProjectListItem } from '@/api/clientPortal'
import { Badge, ProgressBar } from '@/components/ui'
import { paths } from '@/routes/paths'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { projectPriorityVariant, projectStatusVariant } from '@/utils/statusBadge'

export function ClientProjectRow({ project }: { project: ClientProjectListItem }) {
  return (
    <Link
      to={paths.client.projectDetail(project.id)}
      className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-panel p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 sm:flex-row sm:items-center sm:justify-between"
    >
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <h3 className="truncate text-base font-semibold text-slate-900">{project.title}</h3>
          <Badge variant={projectStatusVariant[project.status]}>{formatEnumLabel(project.status)}</Badge>
          <Badge variant={projectPriorityVariant[project.priority]}>{formatEnumLabel(project.priority)}</Badge>
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-sm text-slate-500">
          <Calendar className="size-3.5" aria-hidden="true" />
          {project.deadline ? `Due ${formatDate(project.deadline)}` : 'No deadline set'}
        </div>
      </div>
      <div className="w-full shrink-0 sm:w-40">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Progress</span>
          <span className="font-medium text-slate-700">{Math.round(project.progress_percentage)}%</span>
        </div>
        <ProgressBar value={project.progress_percentage} className="mt-1.5" />
      </div>
    </Link>
  )
}
