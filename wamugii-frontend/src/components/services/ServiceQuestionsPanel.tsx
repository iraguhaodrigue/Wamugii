import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowDown, ArrowUp, HelpCircle, Plus, RotateCcw, Trash2 } from 'lucide-react'
import {
  CHOICE_QUESTION_TYPES,
  QUESTION_TYPES,
  createServiceQuestion,
  deleteServiceQuestion,
  listServiceQuestions,
  updateServiceQuestion,
  type QuestionType,
  type ServiceQuestion,
} from '@/api/services'
import type { ApiError } from '@/lib/apiClient'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  Input,
  Modal,
  Select,
  Skeleton,
} from '@/components/ui'
import { formatEnumLabel } from '@/utils/format'
import { cn } from '@/utils/cn'

export interface ServiceQuestionsPanelProps {
  serviceId: number
}

interface DraftQuestion {
  question_text: string
  question_type: QuestionType
  /** One choice per line while editing — joined/split only at the boundary. */
  optionsText: string
  is_required: boolean
}

const EMPTY_DRAFT: DraftQuestion = {
  question_text: '',
  question_type: 'TEXT',
  optionsText: '',
  is_required: false,
}

function parseOptions(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
}

function toDraft(question: ServiceQuestion): DraftQuestion {
  return {
    question_text: question.question_text,
    question_type: question.question_type,
    optionsText: (question.options ?? []).join('\n'),
    is_required: question.is_required,
  }
}

/**
 * Manage one service's quote questions.
 *
 * Reordering writes `display_order` on the two swapped questions rather than
 * renumbering the whole list — the public form sorts by that column, so two
 * writes are all a move needs.
 */
export function ServiceQuestionsPanel({ serviceId }: ServiceQuestionsPanelProps) {
  const queryClient = useQueryClient()

  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editing, setEditing] = useState<ServiceQuestion | null>(null)
  const [draft, setDraft] = useState<DraftQuestion>(EMPTY_DRAFT)
  const [removing, setRemoving] = useState<ServiceQuestion | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const questionsQuery = useQuery({
    queryKey: ['services', serviceId, 'questions', 'manage'],
    // Soft-deleted ones included so they can be reactivated rather than
    // re-typed; the public form never sees them.
    queryFn: () => listServiceQuestions(serviceId, { include_inactive: true }),
  })

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ['services', serviceId, 'questions'] })
    queryClient.invalidateQueries({ queryKey: ['services', String(serviceId), 'questions'] })
  }

  const saveMutation = useMutation<ServiceQuestion, ApiError, void>({
    mutationFn: () => {
      const isChoice = CHOICE_QUESTION_TYPES.includes(draft.question_type)
      const payload = {
        question_text: draft.question_text.trim(),
        question_type: draft.question_type,
        options: isChoice ? parseOptions(draft.optionsText) : null,
        is_required: draft.is_required,
      }
      if (editing) {
        return updateServiceQuestion(serviceId, editing.id, payload)
      }
      return createServiceQuestion(serviceId, {
        ...payload,
        // Append: one past the current highest, so a new question lands at the
        // bottom of the form instead of colliding on 0.
        display_order: (questionsQuery.data?.length ?? 0) + 1,
      })
    },
    onSuccess: () => {
      refresh()
      setIsFormOpen(false)
      setEditing(null)
      setDraft(EMPTY_DRAFT)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const reorderMutation = useMutation<
    unknown,
    ApiError,
    { a: ServiceQuestion; b: ServiceQuestion }
  >({
    mutationFn: async ({ a, b }) => {
      await updateServiceQuestion(serviceId, a.id, { display_order: b.display_order })
      await updateServiceQuestion(serviceId, b.id, { display_order: a.display_order })
    },
    onSuccess: refresh,
    onError: (err) => setFormError(err.message),
  })

  const removeMutation = useMutation<ServiceQuestion, ApiError, number>({
    mutationFn: (questionId) => deleteServiceQuestion(serviceId, questionId),
    onSuccess: () => {
      refresh()
      setRemoving(null)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const restoreMutation = useMutation<ServiceQuestion, ApiError, number>({
    mutationFn: (questionId) =>
      updateServiceQuestion(serviceId, questionId, { is_active: true }),
    onSuccess: refresh,
    onError: (err) => setFormError(err.message),
  })

  const all = questionsQuery.data ?? []
  const active = all.filter((q) => q.is_active)
  const removed = all.filter((q) => !q.is_active)
  const isChoice = CHOICE_QUESTION_TYPES.includes(draft.question_type)
  const canSave =
    draft.question_text.trim().length > 0 && (!isChoice || parseOptions(draft.optionsText).length > 0)

  function openCreate() {
    setEditing(null)
    setDraft(EMPTY_DRAFT)
    setFormError(null)
    setIsFormOpen(true)
  }

  function openEdit(question: ServiceQuestion) {
    setEditing(question)
    setDraft(toDraft(question))
    setFormError(null)
    setIsFormOpen(true)
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Questions the public quote form asks when someone picks this service. Reorder them to
          change the order they appear in.
        </p>
        <Button
          size="sm"
          className="shrink-0"
          leftIcon={<Plus className="size-4" />}
          onClick={openCreate}
        >
          Add question
        </Button>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      {questionsQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-xl" />
          ))}
        </div>
      ) : questionsQuery.isError ? (
        <ErrorState
          title="Couldn't load the questions"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => questionsQuery.refetch()}
        />
      ) : active.length === 0 ? (
        <EmptyState
          icon={HelpCircle}
          title="No questions yet"
          description="Without questions the quote form shows only the standard fields for this service."
        />
      ) : (
        <ul className="space-y-3">
          {active.map((question, index) => (
            <li
              key={question.id}
              className={cn(
                'rounded-xl border border-slate-200 bg-panel p-4',
                reorderMutation.isPending && 'opacity-60',
              )}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-900">{question.question_text}</p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-2">
                    <Badge variant="info">{formatEnumLabel(question.question_type)}</Badge>
                    {question.is_required ? (
                      <Badge variant="warning">Required</Badge>
                    ) : (
                      <Badge variant="neutral">Optional</Badge>
                    )}
                  </div>
                  {question.options && question.options.length > 0 && (
                    <p className="mt-2 text-xs text-slate-500">
                      Choices: {question.options.join(' · ')}
                    </p>
                  )}
                </div>

                <div className="flex shrink-0 items-center gap-1">
                  <button
                    type="button"
                    aria-label={`Move "${question.question_text}" up`}
                    disabled={index === 0 || reorderMutation.isPending}
                    onClick={() =>
                      reorderMutation.mutate({ a: question, b: active[index - 1]! })
                    }
                    className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <ArrowUp className="size-4" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    aria-label={`Move "${question.question_text}" down`}
                    disabled={index === active.length - 1 || reorderMutation.isPending}
                    onClick={() =>
                      reorderMutation.mutate({ a: question, b: active[index + 1]! })
                    }
                    className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <ArrowDown className="size-4" aria-hidden="true" />
                  </button>
                  <Button size="sm" variant="outline" onClick={() => openEdit(question)}>
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    leftIcon={<Trash2 className="size-4" />}
                    onClick={() => setRemoving(question)}
                  >
                    Remove
                  </Button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      {removed.length > 0 && (
        <div className="rounded-xl border border-dashed border-slate-300 p-4">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Removed ({removed.length})
          </h3>
          <p className="mt-1 text-xs text-slate-500">
            Hidden from the quote form. Quotes already submitted keep their answers.
          </p>
          <ul className="mt-3 space-y-2">
            {removed.map((question) => (
              <li key={question.id} className="flex items-center justify-between gap-3 text-sm">
                <span className="min-w-0 truncate text-slate-500">{question.question_text}</span>
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<RotateCcw className="size-4" />}
                  isLoading={
                    restoreMutation.isPending && restoreMutation.variables === question.id
                  }
                  onClick={() => restoreMutation.mutate(question.id)}
                >
                  Restore
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title={editing ? 'Edit question' : 'Add a question'}
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Question"
            required
            placeholder="e.g. Roughly how many pages do you need?"
            value={draft.question_text}
            onChange={(e) => setDraft((d) => ({ ...d, question_text: e.target.value }))}
          />
          <Select
            label="Answer type"
            options={QUESTION_TYPES.map((t) => ({ value: t, label: formatEnumLabel(t) }))}
            value={draft.question_type}
            onChange={(e) =>
              setDraft((d) => ({ ...d, question_type: e.target.value as QuestionType }))
            }
            hint="Select and Multiselect need a list of choices below"
          />

          {isChoice && (
            <div className="flex flex-col gap-1.5">
              <label
                htmlFor="question-options"
                className="text-sm font-medium text-slate-700"
              >
                Choices<span className="ml-0.5 text-red-600">*</span>
              </label>
              <textarea
                id="question-options"
                rows={5}
                placeholder={'One per line, e.g.\nContact form\nBlog or news\nOnline shop'}
                value={draft.optionsText}
                onChange={(e) => setDraft((d) => ({ ...d, optionsText: e.target.value }))}
                className="w-full resize-y rounded-lg border border-slate-300 bg-panel px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus-visible:border-brand-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              />
              <p className="text-xs text-slate-500">
                {parseOptions(draft.optionsText).length} choice(s). Blank lines are ignored.
              </p>
            </div>
          )}

          <label className="inline-flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-600">
            <input
              type="checkbox"
              className="size-4 rounded border-slate-300 accent-[var(--color-brand-solid)]"
              checked={draft.is_required}
              onChange={(e) => setDraft((d) => ({ ...d, is_required: e.target.checked }))}
            />
            Required — the form won&apos;t submit without an answer
          </label>

          {formError && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </p>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsFormOpen(false)}
              disabled={saveMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              disabled={!canSave}
              isLoading={saveMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {editing ? 'Save question' : 'Add question'}
            </Button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={removing !== null}
        onClose={() => setRemoving(null)}
        onConfirm={() => removing && removeMutation.mutate(removing.id)}
        title="Remove this question?"
        description="It disappears from the quote form straight away. Quotes already submitted keep their answers and the original wording, and you can restore it later."
        confirmLabel="Remove"
        isDanger
        isLoading={removeMutation.isPending}
      />
    </div>
  )
}
