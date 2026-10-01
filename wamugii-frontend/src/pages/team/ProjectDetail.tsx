import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Download, FileText, ListChecks, SearchX } from 'lucide-react'
import { downloadMyProjectFile, getMyProject, type TeamProject } from '@/api/team'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatDate, formatEnumLabel, formatFileSize } from '@/utils/format'
import {
  milestoneStatusVariant,
  projectPriorityVariant,
  projectRoleVariant,
  projectStatusVariant,
} from '@/utils/statusBadge'

/**
 * Technical detail for one assigned project.
 *
 * The payload is `TeamProjectDetail`, which declares no client or billing field,
 * so this page could not render one even by mistake. The 404 path covers both
 * "doesn't exist" and "not assigned to you" — the backend doesn't distinguish
 * them, and neither should this.
 */
export function TeamProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const [downloadError, setDownloadError] = useState<string | null>(null)
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  const projectQuery = useQuery<TeamProject, ApiError>({
    queryKey: ['team', 'projects', 'detail', projectId],
    queryFn: () => getMyProject(projectId!),
    enabled: Boolean(projectId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  async function handleDownload(fileId: number, filename: string) {
    setDownloadError(null)
    setDownloadingId(fileId)
    try {
      await downloadMyProjectFile(projectId!, fileId, filename)
    } catch {
      setDownloadError(`Couldn't download ${filename}. Please try again.`)
    } finally {
      setDownloadingId(null)
    }
  }

  if (projectQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = projectQuery.isError && projectQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Project not found"
        description="This project doesn't exist, or you're not assigned to it."
        action={
          <Link
            to={paths.team.projects}
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

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.team.projects}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Projects
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{project.title}</h1>
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
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Brief</h2>
            <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-slate-700">
              {project.description}
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <ListChecks className="size-4" aria-hidden="true" />
              Milestones
            </h2>
            {project.milestones.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">No milestones set up yet.</p>
            ) : (
              <ol className="mt-4 space-y-3">
                {project.milestones.map((milestone) => (
                  <li
                    key={milestone.id}
                    className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <p className="text-sm font-semibold text-slate-900">{milestone.title}</p>
                      <Badge variant={milestoneStatusVariant[milestone.status]}>
                        {formatEnumLabel(milestone.status)}
                      </Badge>
                    </div>
                    {milestone.description && (
                      <p className="mt-1.5 whitespace-pre-line text-sm text-slate-600">
                        {milestone.description}
                      </p>
                    )}
                    <p className="mt-2 text-xs text-slate-500">
                      {milestone.due_date ? `Due ${formatDate(milestone.due_date)}` : 'No due date'}
                      {milestone.completed_at &&
                        ` · completed ${formatDate(milestone.completed_at)}`}
                    </p>
                  </li>
                ))}
              </ol>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <FileText className="size-4" aria-hidden="true" />
              Files
            </h2>

            {downloadError && (
              <p role="alert" className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {downloadError}
              </p>
            )}

            {project.files.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">No files on this project yet.</p>
            ) : (
              <ul className="mt-4 divide-y divide-slate-100">
                {project.files.map((file) => (
                  <li
                    key={file.id}
                    className="flex flex-wrap items-center justify-between gap-3 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-900">
                        {file.original_filename}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {formatEnumLabel(file.category)} · {formatFileSize(file.file_size)} ·{' '}
                        {formatDate(file.created_at)}
                      </p>
                      {file.description && (
                        <p className="mt-1 text-xs text-slate-500">{file.description}</p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      leftIcon={<Download className="size-4" />}
                      isLoading={downloadingId === file.id}
                      onClick={() => handleDownload(file.id, file.original_filename)}
                    >
                      Download
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Your role</dt>
              <dd>
                <Badge variant={projectRoleVariant[project.my_role]}>
                  {formatEnumLabel(project.my_role)}
                </Badge>
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Started</dt>
              <dd className="font-medium text-slate-900">{formatDate(project.start_date)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Deadline</dt>
              <dd className="font-medium text-slate-900">{formatDate(project.deadline)}</dd>
            </div>
            {project.completed_at && (
              <div>
                <dt className="text-slate-500">Completed</dt>
                <dd className="font-medium text-slate-900">{formatDate(project.completed_at)}</dd>
              </div>
            )}
            <div>
              <dt className="text-slate-500">Last update</dt>
              <dd className="font-medium text-slate-900">{formatDate(project.updated_at)}</dd>
            </div>
          </dl>

          <p className="border-t border-slate-100 pt-4 text-xs text-slate-500">
            Client and commercial details are handled by the WAMUGII team and aren&apos;t part of
            your view.
          </p>
        </aside>
      </div>
    </div>
  )
}
