import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Pencil, SearchX, Trash2 } from 'lucide-react'
import { deactivateProject, getProject, updateProject, type ProjectPriority, type ProjectRead, type ProjectStatus } from '@/api/projects'
import { listServices } from '@/api/services'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Input, Select, Skeleton, Textarea } from '@/components/ui'
import { MilestonesPanel } from '@/components/milestones/MilestonesPanel'
import { FilesPanel } from '@/components/files/FilesPanel'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { projectPriorityVariant, projectStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const PROJECT_STATUSES: ProjectStatus[] = [
  'PENDING',
  'PLANNING',
  'IN_PROGRESS',
  'ON_HOLD',
  'TESTING',
  'CLIENT_REVIEW',
  'COMPLETED',
  'CANCELLED',
]
const PROJECT_PRIORITIES: ProjectPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']

const editSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  status: z.enum(['PENDING', 'PLANNING', 'IN_PROGRESS', 'ON_HOLD', 'TESTING', 'CLIENT_REVIEW', 'COMPLETED', 'CANCELLED']),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  budget: z.string().optional(),
  amount_paid: z.string().optional(),
  start_date: z.string().optional(),
  deadline: z.string().optional(),
})
type EditFormValues = z.infer<typeof editSchema>

type Tab = 'overview' | 'milestones' | 'files'

function EditProjectForm({
  project,
  onSaved,
  onCancel,
}: {
  project: ProjectRead
  onSaved: (updated: ProjectRead) => void
  onCancel: () => void
}) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EditFormValues>({
    resolver: zodResolver(editSchema),
    defaultValues: {
      title: project.title,
      description: project.description,
      status: project.status,
      priority: project.priority,
      budget: project.budget ?? '',
      amount_paid: project.amount_paid,
      start_date: project.start_date?.slice(0, 10) ?? '',
      deadline: project.deadline?.slice(0, 10) ?? '',
    },
  })

  const mutation = useMutation({
    mutationFn: (values: EditFormValues) =>
      updateProject(project.id, {
        title: values.title,
        description: values.description,
        status: values.status,
        priority: values.priority,
        budget: values.budget || null,
        amount_paid: values.amount_paid || null,
        start_date: values.start_date || null,
        deadline: values.deadline || null,
      }),
    onSuccess: onSaved,
    onError: (err: ApiError) => setFormError(err.message),
  })

  return (
    <form onSubmit={handleSubmit((values) => mutation.mutate(values))} className="space-y-4" noValidate>
      <Input label="Title" required error={errors.title?.message} {...register('title')} />
      <Textarea label="Description" required rows={4} error={errors.description?.message} {...register('description')} />
      <div className="grid gap-4 sm:grid-cols-2">
        <Select label="Status" options={PROJECT_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))} {...register('status')} />
        <Select label="Priority" options={PROJECT_PRIORITIES.map((p) => ({ value: p, label: formatEnumLabel(p) }))} {...register('priority')} />
        <Input label="Budget" type="number" step="0.01" min="0" hint="Optional" {...register('budget')} />
        <Input label="Amount paid" type="number" step="0.01" min="0" {...register('amount_paid')} />
        <Input label="Start date" type="date" hint="Optional" {...register('start_date')} />
        <Input label="Deadline" type="date" hint="Optional" {...register('deadline')} />
      </div>
      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}
      <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting || mutation.isPending}>
          Save Changes
        </Button>
      </div>
    </form>
  )
}

export function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { usersMap } = useUsersMap()
  const { data: services } = useQuery({ queryKey: ['services', 'lookup'], queryFn: () => listServices() })
  const servicesMap = useMemo(() => new Map((services ?? []).map((s) => [s.id, s.name])), [services])

  const [tab, setTab] = useState<Tab>('overview')
  const [isEditing, setIsEditing] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)

  const projectQuery = useQuery<ProjectRead, ApiError>({
    queryKey: ['projects', 'detail', projectId],
    queryFn: () => getProject(projectId!),
    enabled: Boolean(projectId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  usePageTitle(projectQuery.data?.title ?? 'Project')

  const deleteMutation = useMutation({
    mutationFn: () => deactivateProject(projectId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      navigate(isAdmin ? paths.admin.projects : paths.staff.projects)
    },
  })

  const listPath = isAdmin ? paths.admin.projects : paths.staff.projects

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
        description="This project doesn't exist or was deactivated."
        action={
          <Link to={listPath} className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700">
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Projects
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
  const client = usersMap.get(project.client_id)
  const budget = formatMoney(project.budget)
  const amountPaid = formatMoney(project.amount_paid)

  const tabs: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'milestones', label: 'Milestones' },
    { key: 'files', label: 'Files' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <Link to={listPath} className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600">
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Projects
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{project.title}</h1>
            <Badge variant={projectStatusVariant[project.status]}>{formatEnumLabel(project.status)}</Badge>
            <Badge variant={projectPriorityVariant[project.priority]}>{formatEnumLabel(project.priority)}</Badge>
          </div>
          {tab === 'overview' && !isEditing && (
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" leftIcon={<Pencil className="size-4" />} onClick={() => setIsEditing(true)}>
                Edit
              </Button>
              {isAdmin && (
                <Button size="sm" variant="danger" leftIcon={<Trash2 className="size-4" />} onClick={() => setIsDeleteOpen(true)}>
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="border-b border-slate-200">
        <nav className="-mb-px flex gap-6" aria-label="Project detail tabs">
          {tabs.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={cn(
                'border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                tab === t.key ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-700',
              )}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'overview' &&
        (isEditing ? (
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <EditProjectForm
              project={project}
              onCancel={() => setIsEditing(false)}
              onSaved={(updated) => {
                queryClient.setQueryData(['projects', 'detail', projectId], updated)
                queryClient.invalidateQueries({ queryKey: ['projects'] })
                setIsEditing(false)
              }}
            />
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm lg:col-span-2">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Description</h2>
              <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-600">{project.description}</p>
            </div>
            <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
              <dl className="space-y-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Client</dt>
                  <dd className="text-right font-medium text-slate-900">{client?.full_name ?? `#${project.client_id}`}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Service</dt>
                  <dd className="text-right font-medium text-slate-900">
                    {project.service_id ? (servicesMap.get(project.service_id) ?? `#${project.service_id}`) : 'None'}
                  </dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Budget</dt>
                  <dd className="font-medium text-slate-900">{budget ?? 'Not set'}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Amount paid</dt>
                  <dd className="font-medium text-slate-900">{amountPaid ?? '—'}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Start date</dt>
                  <dd className="font-medium text-slate-900">{formatDate(project.start_date)}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Deadline</dt>
                  <dd className="font-medium text-slate-900">{formatDate(project.deadline)}</dd>
                </div>
                <div className="flex items-center justify-between gap-3">
                  <dt className="text-slate-500">Created</dt>
                  <dd className="font-medium text-slate-900">{formatDate(project.created_at)}</dd>
                </div>
              </dl>
            </div>
          </div>
        ))}

      {tab === 'milestones' && <MilestonesPanel projectId={project.id} />}
      {tab === 'files' && <FilesPanel projectId={project.id} />}

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this project?"
        description="This deactivates the project. Clients will no longer be able to see it."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
