import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronDown, ChevronUp, Pencil, Plus, Trash2 } from 'lucide-react'
import {
  createMilestone,
  deleteMilestone,
  getProjectProgress,
  listMilestones,
  reorderMilestones,
  updateMilestone,
  type MilestoneStatus,
  type ProjectMilestoneListItem,
} from '@/api/projectMilestones'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Input, ProgressBar, Select, Skeleton, Textarea } from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { milestoneStatusVariant } from '@/utils/statusBadge'

const MILESTONE_STATUSES: MilestoneStatus[] = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', 'CANCELLED']
const statusOptions = MILESTONE_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
  status: z.enum(['PENDING', 'IN_PROGRESS', 'COMPLETED', 'ON_HOLD', 'CANCELLED']),
  start_date: z.string().optional(),
  due_date: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

function MilestoneForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSaving,
  submitLabel,
}: {
  defaultValues: FormValues
  onSubmit: (values: FormValues) => void
  onCancel: () => void
  isSaving: boolean
  submitLabel: string
}) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4" noValidate>
      <Input label="Title" required error={errors.title?.message} {...register('title')} />
      <Textarea label="Description" rows={2} hint="Optional" {...register('description')} />
      <div className="grid gap-3 sm:grid-cols-3">
        <Select label="Status" options={statusOptions} {...register('status')} />
        <Input label="Start date" type="date" hint="Optional" {...register('start_date')} />
        <Input label="Due date" type="date" hint="Optional" {...register('due_date')} />
      </div>
      <div className="flex justify-end gap-2 pt-1">
        <Button type="button" variant="outline" size="sm" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" size="sm" isLoading={isSaving}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}

export function MilestonesPanel({ projectId }: { projectId: number }) {
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()

  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const milestonesQuery = useQuery({
    queryKey: ['projects', projectId, 'milestones'],
    queryFn: () => listMilestones(projectId),
  })

  const progressQuery = useQuery({
    queryKey: ['projects', projectId, 'progress'],
    queryFn: () => getProjectProgress(projectId),
  })

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'milestones'] })
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'progress'] })
  }

  const createMutation = useMutation({
    mutationFn: (values: FormValues) =>
      createMilestone(projectId, {
        title: values.title,
        description: values.description || '',
        status: values.status,
        start_date: values.start_date || null,
        due_date: values.due_date || null,
      }),
    onSuccess: () => {
      setIsCreating(false)
      setFormError(null)
      invalidate()
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: FormValues }) =>
      updateMilestone(projectId, id, {
        title: values.title,
        description: values.description || '',
        status: values.status,
        start_date: values.start_date || null,
        due_date: values.due_date || null,
      }),
    onSuccess: () => {
      setEditingId(null)
      setFormError(null)
      invalidate()
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteMilestone(projectId, id),
    onSuccess: () => {
      setPendingDeleteId(null)
      invalidate()
    },
  })

  const reorderMutation = useMutation({
    mutationFn: (items: { id: number; display_order: number }[]) => reorderMilestones(projectId, items),
    onSuccess: () => invalidate(),
  })

  const milestones = milestonesQuery.data ?? []

  function move(index: number, direction: -1 | 1) {
    const target = index + direction
    if (target < 0 || target >= milestones.length) return
    const a = milestones[index]
    const b = milestones[target]
    if (!a || !b) return
    reorderMutation.mutate([
      { id: a.id, display_order: b.display_order },
      { id: b.id, display_order: a.display_order },
    ])
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-panel p-5 shadow-sm">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-slate-700">Progress</span>
          {progressQuery.data && (
            <span className="text-slate-500">
              {progressQuery.data.completed_milestones} of {progressQuery.data.total_milestones} milestones complete
            </span>
          )}
        </div>
        {progressQuery.data ? (
          <>
            <ProgressBar value={progressQuery.data.progress_percentage} className="mt-2" />
            <p className="mt-1 text-right text-xs text-slate-500">{Math.round(progressQuery.data.progress_percentage)}%</p>
          </>
        ) : (
          <Skeleton className="mt-2 h-2 w-full rounded-full" />
        )}
      </div>

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Milestones</h3>
        {!isCreating && (
          <Button size="sm" variant="outline" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreating(true)}>
            Add Milestone
          </Button>
        )}
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      {isCreating && (
        <MilestoneForm
          defaultValues={{ title: '', description: '', status: 'PENDING', start_date: '', due_date: '' }}
          onSubmit={(values) => createMutation.mutate(values)}
          onCancel={() => {
            setIsCreating(false)
            setFormError(null)
          }}
          isSaving={createMutation.isPending}
          submitLabel="Add Milestone"
        />
      )}

      {milestonesQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-lg" />
          ))}
        </div>
      ) : milestonesQuery.isError ? (
        <ErrorState title="Couldn't load milestones" message="Please try again." onRetry={() => milestonesQuery.refetch()} />
      ) : milestones.length === 0 && !isCreating ? (
        <EmptyState title="No milestones yet" description="Break this project down into trackable steps." />
      ) : (
        <ul className="space-y-3">
          {milestones.map((milestone: ProjectMilestoneListItem, index) =>
            editingId === milestone.id ? (
              <li key={milestone.id}>
                <MilestoneForm
                  defaultValues={{
                    title: milestone.title,
                    description: milestone.description,
                    status: milestone.status,
                    start_date: milestone.start_date?.slice(0, 10) ?? '',
                    due_date: milestone.due_date?.slice(0, 10) ?? '',
                  }}
                  onSubmit={(values) => updateMutation.mutate({ id: milestone.id, values })}
                  onCancel={() => {
                    setEditingId(null)
                    setFormError(null)
                  }}
                  isSaving={updateMutation.isPending}
                  submitLabel="Save Changes"
                />
              </li>
            ) : (
              <li
                key={milestone.id}
                className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-panel p-4 shadow-sm sm:flex-row sm:items-start sm:justify-between"
              >
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="text-sm font-semibold text-slate-900">{milestone.title}</h4>
                    <Badge variant={milestoneStatusVariant[milestone.status]}>{formatEnumLabel(milestone.status)}</Badge>
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
                <div className="flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    onClick={() => move(index, -1)}
                    disabled={index === 0 || reorderMutation.isPending}
                    aria-label="Move up"
                    className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <ChevronUp className="size-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => move(index, 1)}
                    disabled={index === milestones.length - 1 || reorderMutation.isPending}
                    aria-label="Move down"
                    className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <ChevronDown className="size-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setEditingId(milestone.id)
                      setFormError(null)
                    }}
                    aria-label="Edit milestone"
                    className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
                  >
                    <Pencil className="size-4" />
                  </button>
                  {isAdmin && (
                    <button
                      type="button"
                      onClick={() => setPendingDeleteId(milestone.id)}
                      aria-label="Delete milestone"
                      className="rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 className="size-4" />
                    </button>
                  )}
                </div>
              </li>
            ),
          )}
        </ul>
      )}

      <ConfirmDialog
        isOpen={pendingDeleteId !== null}
        onClose={() => setPendingDeleteId(null)}
        onConfirm={() => pendingDeleteId !== null && deleteMutation.mutate(pendingDeleteId)}
        title="Delete this milestone?"
        description="This removes it from the project's milestone list. This can't be undone from the UI."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
