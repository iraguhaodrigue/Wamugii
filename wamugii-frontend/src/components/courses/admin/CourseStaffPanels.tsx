import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2,
  MessageCircleQuestion,
  Pencil,
  Plus,
  Send,
  Sparkles,
  Trash2,
  UserPlus,
  Users,
  XCircle,
} from 'lucide-react'
import {
  addExamQuestions,
  aiDraftQuestions,
  answerQuestion,
  assignInstructor,
  deleteExamQuestion,
  editExamQuestion,
  getExamBank,
  hideQuestion,
  listCourseQuestions,
  listExamAttempts,
  listInstructors,
  removeInstructor,
  updateExamSettings,
  type ExamQuestionAdmin,
  type ExamQuestionKind,
  type ExamQuestionWrite,
  type ExamSettings,
  type LessonQuestion,
} from '@/api/exams'
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
  Textarea,
} from '@/components/ui'
import { cn } from '@/utils/cn'

const KINDS: { value: ExamQuestionKind; label: string }[] = [
  { value: 'SINGLE', label: 'Single answer' },
  { value: 'MULTIPLE', label: 'Multiple answers' },
  { value: 'TRUE_FALSE', label: 'True / false' },
  { value: 'FILL_BLANK', label: 'Fill in the blank' },
]
const KIND_LABEL = Object.fromEntries(KINDS.map((k) => [k.value, k.label])) as Record<string, string>

function when(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

// =============================================================================
// Exam bank + rules
// =============================================================================

const BLANK: ExamQuestionWrite = { kind: 'SINGLE', question: '', options: ['', '', '', ''], correct: [0], explanation: '', topic: null, is_active: true }

export function ExamManager({ courseId, topics }: { courseId: number; topics: string[] }) {
  const queryClient = useQueryClient()
  const key = ['courses', 'admin', courseId, 'exam']
  const bank = useQuery({ queryKey: key, queryFn: () => getExamBank(courseId) })
  const [kindFilter, setKindFilter] = useState<string>('')
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<{ id: number | null; draft: ExamQuestionWrite } | null>(null)
  const [removing, setRemoving] = useState<ExamQuestionAdmin | null>(null)
  const [aiOpen, setAiOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = () => queryClient.invalidateQueries({ queryKey: key })
  const save = useMutation<unknown, ApiError, { id: number | null; draft: ExamQuestionWrite }>({
    mutationFn: ({ id, draft }) => (id ? editExamQuestion(courseId, id, draft) : addExamQuestions(courseId, [draft])),
    onSuccess: () => {
      refresh()
      setEditing(null)
      setError(null)
    },
    onError: (e) => setError(e.message),
  })
  const remove = useMutation<unknown, ApiError, number>({
    mutationFn: (id) => deleteExamQuestion(courseId, id),
    onSuccess: () => {
      refresh()
      setRemoving(null)
    },
  })

  const filtered = useMemo(() => {
    const s = search.trim().toLowerCase()
    return (bank.data?.questions ?? []).filter(
      (q) => (!kindFilter || q.kind === kindFilter) && (!s || q.question.toLowerCase().includes(s) || (q.topic ?? '').toLowerCase().includes(s)),
    )
  }, [bank.data, kindFilter, search])

  if (bank.isLoading) return <Skeleton className="h-64 rounded-xl" />
  if (bank.isError || !bank.data) return <ErrorState title="Couldn't load the exam" message="Please try again." onRetry={() => bank.refetch()} />
  const { counts, settings } = bank.data

  return (
    <div className="space-y-6">
      <ExamRules courseId={courseId} settings={settings} total={counts.total ?? 0} onSaved={refresh} />

      <div className="rounded-xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)]">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Question bank</h2>
            <p className="mt-1 text-sm text-slate-500">
              Each attempt draws {settings.exam_question_count} random questions from the active ones below, mixed by type.
              Keep the bank bigger than the exam so every attempt is different.
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              {KINDS.map((k) => (
                <span key={k.value} className="rounded-full border border-slate-200 px-2.5 py-1 text-slate-600">
                  {k.label}: <b className="text-slate-900">{counts[k.value] ?? 0}</b>
                </span>
              ))}
              <span className="rounded-full bg-brand-50 px-2.5 py-1 font-semibold text-brand-700">Total active: {counts.total ?? 0}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button size="sm" variant="outline" leftIcon={<Sparkles className="size-4" />} onClick={() => setAiOpen(true)}>
              Draft with AI
            </Button>
            <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setEditing({ id: null, draft: { ...BLANK, options: ['', '', '', ''] } })}>
              Add question
            </Button>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-[1fr_14rem]">
          <Input placeholder="Search questions or topics" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Search questions" />
          <Select aria-label="Filter by type" options={[{ value: '', label: 'All types' }, ...KINDS]} value={kindFilter} onChange={(e) => setKindFilter(e.target.value)} />
        </div>

        {filtered.length === 0 ? (
          <p className="mt-6 text-sm text-slate-500">No questions match.</p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-100">
            {filtered.map((q) => (
              <li key={q.id} className={cn('flex items-start gap-3 py-3', !q.is_active && 'opacity-50')}>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                    <Badge variant="info">{KIND_LABEL[q.kind]}</Badge>
                    {q.topic && <span className="text-slate-400">{q.topic}</span>}
                    {!q.is_active && <Badge variant="neutral">Hidden</Badge>}
                  </div>
                  <p className="mt-1 text-sm text-slate-900">{q.question}</p>
                  <p className="mt-0.5 text-xs text-emerald-600">
                    Answer:{' '}
                    {q.kind === 'FILL_BLANK'
                      ? (q.correct as string[]).join(' / ')
                      : (q.correct as number[]).map((i) => q.options[i]).join(' + ')}
                  </p>
                </div>
                <div className="flex shrink-0 gap-1">
                  <button
                    type="button"
                    aria-label="Edit question"
                    className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
                    onClick={() =>
                      setEditing({
                        id: q.id,
                        draft: { kind: q.kind, question: q.question, options: [...q.options], correct: [...q.correct], explanation: q.explanation, topic: q.topic, is_active: q.is_active },
                      })
                    }
                  >
                    <Pencil className="size-4" />
                  </button>
                  <button type="button" aria-label="Remove question" className="rounded-md p-1.5 text-slate-500 hover:bg-red-50 hover:text-red-600" onClick={() => setRemoving(q)}>
                    <Trash2 className="size-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <QuestionEditor
        open={Boolean(editing)}
        draft={editing?.draft ?? BLANK}
        isNew={!editing?.id}
        topics={topics}
        error={error}
        saving={save.isPending}
        onChange={(draft) => setEditing((e) => (e ? { ...e, draft } : e))}
        onClose={() => {
          setEditing(null)
          setError(null)
        }}
        onSave={() => editing && save.mutate(editing)}
      />
      <AiDraftDialog open={aiOpen} courseId={courseId} available={bank.data.ai_drafting_available} onClose={() => setAiOpen(false)} onSaved={refresh} />
      <ConfirmDialog
        isOpen={Boolean(removing)}
        onClose={() => setRemoving(null)}
        onConfirm={() => removing && remove.mutate(removing.id)}
        title="Remove this question?"
        description="Questions already used in an exam are hidden instead of deleted, so past results stay correct."
        confirmLabel="Remove"
        isDanger
        isLoading={remove.isPending}
      />
    </div>
  )
}

function ExamRules({ courseId, settings, total, onSaved }: { courseId: number; settings: ExamSettings; total: number; onSaved: () => void }) {
  const [draft, setDraft] = useState<ExamSettings | null>(null)
  const working = draft ?? settings
  const save = useMutation<ExamSettings, ApiError, ExamSettings>({
    mutationFn: (s) => updateExamSettings(courseId, s),
    onSuccess: () => {
      setDraft(null)
      onSaved()
    },
  })
  const field = (key: keyof ExamSettings, label: string, hint: string) => (
    <Input
      label={label}
      hint={hint}
      type="number"
      min="0"
      value={String(working[key])}
      onChange={(e) => setDraft({ ...working, [key]: Number(e.target.value || 0) })}
    />
  )
  return (
    <div className="rounded-xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)]">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Final exam rules</h2>
      <p className="mt-1 text-sm text-slate-500">
        {total === 0
          ? 'This course has no exam questions yet, so the certificate needs the lessons only. Add questions to switch the final exam on.'
          : 'Students unlock the exam after finishing every lesson. Passing it unlocks the certificate.'}
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        {field('exam_question_count', 'Questions per exam', 'Drawn at random')}
        {field('exam_minutes', 'Time (minutes)', 'Auto-submits at 0:00')}
        {field('exam_pass_percent', 'Pass mark (%)', 'Needed for the certificate')}
        {field('exam_max_attempts', 'Attempts', 'Per student')}
        {field('exam_cooldown_hours', 'Hours between attempts', '0 = no waiting')}
        {field('exam_max_leaves', 'Screen leaves allowed', 'The last one submits')}
      </div>
      {save.isError && <p className="mt-3 text-sm text-red-600">{save.error.message}</p>}
      {draft && (
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" onClick={() => setDraft(null)}>Cancel</Button>
          <Button isLoading={save.isPending} onClick={() => save.mutate(working)}>Save rules</Button>
        </div>
      )}
    </div>
  )
}

function QuestionEditor({
  open,
  draft,
  isNew,
  topics,
  error,
  saving,
  onChange,
  onClose,
  onSave,
}: {
  open: boolean
  draft: ExamQuestionWrite
  isNew: boolean
  topics: string[]
  error: string | null
  saving: boolean
  onChange: (d: ExamQuestionWrite) => void
  onClose: () => void
  onSave: () => void
}) {
  const choice = draft.kind !== 'FILL_BLANK'
  const options = draft.options ?? []
  const correct = new Set((draft.correct as (number | string)[]).map((c) => Number(c)))
  const setKind = (kind: ExamQuestionKind) => {
    if (kind === 'TRUE_FALSE') onChange({ ...draft, kind, options: ['True', 'False'], correct: [0] })
    else if (kind === 'FILL_BLANK') onChange({ ...draft, kind, options: [], correct: [''] })
    else onChange({ ...draft, kind, options: options.length >= 2 && draft.kind !== 'TRUE_FALSE' ? options : ['', '', '', ''], correct: [0] })
  }
  return (
    <Modal isOpen={open} onClose={onClose} title={isNew ? 'Add exam question' : 'Edit exam question'} size="lg">
      <div className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <Select label="Type" options={KINDS} value={draft.kind} onChange={(e) => setKind(e.target.value as ExamQuestionKind)} />
          <Select
            label="Topic (week)"
            options={[{ value: '', label: 'No topic' }, ...topics.map((t) => ({ value: t, label: t }))]}
            value={draft.topic ?? ''}
            onChange={(e) => onChange({ ...draft, topic: e.target.value || null })}
          />
        </div>
        <Textarea
          label={draft.kind === 'TRUE_FALSE' ? 'Statement' : 'Question'}
          rows={3}
          hint={draft.kind === 'FILL_BLANK' ? 'Write the sentence and mark the missing part with ___ (three underscores).' : undefined}
          value={draft.question}
          onChange={(e) => onChange({ ...draft, question: e.target.value })}
        />
        {choice ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-700">
              Options — tick the {draft.kind === 'MULTIPLE' ? 'correct options (2 or more)' : 'correct option'}
            </p>
            {options.map((opt, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  type={draft.kind === 'MULTIPLE' ? 'checkbox' : 'radio'}
                  name="correct"
                  aria-label={`Option ${i + 1} is correct`}
                  className="size-4 accent-[var(--color-brand-solid)]"
                  checked={correct.has(i)}
                  onChange={() => {
                    if (draft.kind === 'MULTIPLE') {
                      const next = new Set(correct)
                      if (next.has(i)) next.delete(i)
                      else next.add(i)
                      onChange({ ...draft, correct: [...next].sort() })
                    } else onChange({ ...draft, correct: [i] })
                  }}
                />
                <Input
                  aria-label={`Option ${i + 1}`}
                  className="flex-1"
                  value={opt}
                  disabled={draft.kind === 'TRUE_FALSE'}
                  onChange={(e) => onChange({ ...draft, options: options.map((o, j) => (j === i ? e.target.value : o)) })}
                />
                {draft.kind !== 'TRUE_FALSE' && options.length > 2 && (
                  <button
                    type="button"
                    aria-label="Remove option"
                    className="rounded p-1 text-slate-400 hover:text-red-600"
                    onClick={() =>
                      onChange({
                        ...draft,
                        options: options.filter((_, j) => j !== i),
                        correct: [...correct].filter((c) => c !== i).map((c) => (c > i ? c - 1 : c)),
                      })
                    }
                  >
                    <XCircle className="size-4" />
                  </button>
                )}
              </div>
            ))}
            {draft.kind !== 'TRUE_FALSE' && options.length < 8 && (
              <Button size="sm" variant="ghost" leftIcon={<Plus className="size-4" />} onClick={() => onChange({ ...draft, options: [...options, ''] })}>
                Add option
              </Button>
            )}
          </div>
        ) : (
          <Input
            label="Accepted answers"
            hint="Separate different accepted answers with |   e.g.  0 | zero. Capital letters and extra spaces are ignored."
            value={(draft.correct as string[]).join(' | ')}
            onChange={(e) => onChange({ ...draft, correct: e.target.value.split('|').map((s) => s.trim()) })}
          />
        )}
        <Textarea label="Explanation (for instructors)" rows={2} value={draft.explanation ?? ''} onChange={(e) => onChange({ ...draft, explanation: e.target.value })} />
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" className="size-4" checked={draft.is_active ?? true} onChange={(e) => onChange({ ...draft, is_active: e.target.checked })} />
          Active (can appear in exams)
        </label>
        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
        <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button isLoading={saving} onClick={onSave}>{isNew ? 'Add question' : 'Save question'}</Button>
        </div>
      </div>
    </Modal>
  )
}

function AiDraftDialog({ open, courseId, available, onClose, onSaved }: { open: boolean; courseId: number; available: boolean; onClose: () => void; onSaved: () => void }) {
  const [count, setCount] = useState(10)
  const [drafts, setDrafts] = useState<ExamQuestionWrite[]>([])
  const [keep, setKeep] = useState<Set<number>>(new Set())
  const draft = useMutation({
    mutationFn: () => aiDraftQuestions(courseId, { count }),
    onSuccess: (r) => {
      setDrafts(r.drafts)
      setKeep(new Set(r.drafts.map((_, i) => i)))
    },
  })
  const save = useMutation({
    mutationFn: () => addExamQuestions(courseId, drafts.filter((_, i) => keep.has(i))),
    onSuccess: () => {
      onSaved()
      setDrafts([])
      onClose()
    },
  })
  return (
    <Modal isOpen={open} onClose={onClose} title="Draft questions with AI" size="lg">
      {!available ? (
        <div className="space-y-3 text-sm text-slate-600">
          <p>AI drafting is not switched on for this website yet.</p>
          <p>
            To switch it on, the server administrator adds an <code className="rounded bg-slate-100 px-1">ANTHROPIC_API_KEY</code> to the backend
            settings. AI then reads the lesson notes and drafts questions of all four types for you to review.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            AI reads this course's lesson notes and drafts questions. <b>Nothing is saved until you choose.</b> Check every question and answer — you are responsible for what students see.
          </p>
          <div className="flex items-end gap-3">
            <Input label="How many" type="number" min="1" max="30" value={String(count)} onChange={(e) => setCount(Math.min(30, Math.max(1, Number(e.target.value || 1))))} />
            <Button leftIcon={<Sparkles className="size-4" />} isLoading={draft.isPending} onClick={() => draft.mutate()}>
              Draft questions
            </Button>
          </div>
          {draft.isError && <p className="text-sm text-red-600">{(draft.error as unknown as ApiError).message}</p>}
          {drafts.length > 0 && (
            <>
              <ul className="max-h-[50vh] space-y-2 overflow-y-auto pr-1">
                {drafts.map((d, i) => (
                  <li key={i} className="flex gap-3 rounded-lg border border-slate-200 p-3 text-sm">
                    <input
                      type="checkbox"
                      aria-label="Keep this draft"
                      className="mt-1 size-4"
                      checked={keep.has(i)}
                      onChange={() =>
                        setKeep((prev) => {
                          const next = new Set(prev)
                          if (next.has(i)) next.delete(i)
                          else next.add(i)
                          return next
                        })
                      }
                    />
                    <div className="min-w-0">
                      <Badge variant="info">{KIND_LABEL[d.kind]}</Badge>
                      <p className="mt-1 text-slate-900">{d.question}</p>
                      {d.kind !== 'FILL_BLANK' && (
                        <ul className="mt-1 text-xs text-slate-500">
                          {(d.options ?? []).map((o, j) => (
                            <li key={j} className={cn((d.correct as number[]).includes(j) && 'font-semibold text-emerald-600')}>
                              {(d.correct as number[]).includes(j) ? '✓' : '·'} {o}
                            </li>
                          ))}
                        </ul>
                      )}
                      {d.kind === 'FILL_BLANK' && <p className="mt-1 text-xs text-emerald-600">Answer: {(d.correct as string[]).join(' / ')}</p>}
                    </div>
                  </li>
                ))}
              </ul>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setDrafts([])}>Discard all</Button>
                <Button isLoading={save.isPending} disabled={keep.size === 0} onClick={() => save.mutate()}>
                  Save {keep.size} question{keep.size === 1 ? '' : 's'}
                </Button>
              </div>
            </>
          )}
        </div>
      )}
    </Modal>
  )
}

// =============================================================================
// Exam results
// =============================================================================

const REASON: Record<string, string> = { STUDENT: 'Submitted', LEAVE_LIMIT: 'Auto: left screen', TIME_UP: 'Auto: time up' }

export function ExamResults({ courseId }: { courseId: number }) {
  const q = useQuery({ queryKey: ['courses', 'admin', courseId, 'exam-attempts'], queryFn: () => listExamAttempts(courseId) })
  const [open, setOpen] = useState<number | null>(null)
  if (q.isLoading) return <Skeleton className="h-48 rounded-xl" />
  if (q.isError) return <ErrorState title="Couldn't load results" message="Please try again." onRetry={() => q.refetch()} />
  if (!q.data?.length) return <EmptyState icon={CheckCircle2} title="No exam attempts yet" description="Results appear here as students take the final exam." />
  return (
    <ul className="space-y-2">
      {q.data.map((a) => (
        <li key={a.id} className="rounded-xl border border-slate-200 bg-panel">
          <button type="button" className="flex w-full flex-wrap items-center gap-3 p-4 text-left" onClick={() => setOpen(open === a.id ? null : a.id)}>
            <span className="min-w-0 flex-1">
              <span className="block font-medium text-slate-900">{a.student_name || `Student #${a.client_id}`}</span>
              <span className="text-xs text-slate-500">{a.student_email} · {when(a.started_at)}</span>
            </span>
            {a.status === 'IN_PROGRESS' ? (
              <Badge variant="warning">In progress</Badge>
            ) : (
              <span className={cn('text-sm font-semibold', a.passed ? 'text-emerald-600' : 'text-red-600')}>
                {a.percent}% · {a.passed ? 'Passed' : 'Not passed'}
              </span>
            )}
            {a.submit_reason && <Badge variant={a.submit_reason === 'STUDENT' ? 'neutral' : 'warning'}>{REASON[a.submit_reason] ?? a.submit_reason}</Badge>}
            <Badge variant={a.leave_count > 0 ? 'danger' : 'success'}>Left screen {a.leave_count}×</Badge>
          </button>
          {open === a.id && (
            <div className="grid gap-4 border-t border-slate-100 p-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Score by topic</p>
                <ul className="mt-2 space-y-1 text-sm">
                  {(a.topic_scores ?? []).map((t) => (
                    <li key={t.topic} className="flex justify-between gap-2">
                      <span className="text-slate-600">{t.topic}</span>
                      <span className="font-medium text-slate-900">{t.correct}/{t.total}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Exam-screen log</p>
                <ul className="mt-2 max-h-48 space-y-1 overflow-y-auto text-xs">
                  {(a.events ?? []).map((e, i) => (
                    <li key={i} className={cn('flex justify-between gap-2', e.type === 'leave' ? 'text-red-600' : 'text-slate-500')}>
                      <span>{String(e.type)}{e.detail ? ` · ${String(e.detail)}` : ''}</span>
                      <span>{e.at ? new Date(String(e.at)).toLocaleTimeString() : ''}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </li>
      ))}
    </ul>
  )
}

// =============================================================================
// Student questions (Q&A inbox)
// =============================================================================

export function QuestionsInbox({
  courseId,
  load,
  queryKey,
  courseTitles,
}: {
  courseId?: number
  load?: (unanswered: boolean) => Promise<LessonQuestion[]>
  queryKey?: unknown[]
  /** When given, each question shows its course name (the instructor's all-courses inbox). */
  courseTitles?: Record<number, string>
}) {
  const [onlyOpen, setOnlyOpen] = useState(true)
  const key = [...(queryKey ?? ['courses', 'admin', courseId, 'questions']), onlyOpen]
  const q = useQuery({ queryKey: key, queryFn: () => (load ? load(onlyOpen) : listCourseQuestions(courseId!, onlyOpen)) })
  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {[true, false].map((v) => (
          <button
            key={String(v)}
            type="button"
            onClick={() => setOnlyOpen(v)}
            className={cn('rounded-full px-3 py-1 text-sm font-medium', onlyOpen === v ? 'bg-[var(--color-brand-solid)] text-white' : 'bg-slate-100 text-slate-600')}
          >
            {v ? 'Waiting for an answer' : 'All questions'}
          </button>
        ))}
      </div>
      {q.isLoading ? (
        <Skeleton className="h-32 rounded-xl" />
      ) : q.isError ? (
        <ErrorState title="Couldn't load questions" message="Please try again." onRetry={() => q.refetch()} />
      ) : !q.data?.length ? (
        <EmptyState icon={MessageCircleQuestion} title={onlyOpen ? 'No questions waiting' : 'No questions yet'} description="Students ask questions under each lesson. You get an email when they do." />
      ) : (
        <ul className="space-y-3">
          {q.data.map((item) => (
            <QuestionItem key={item.id} item={item} courseTitle={courseTitles?.[item.course_id]} onDone={() => q.refetch()} />
          ))}
        </ul>
      )}
    </div>
  )
}

function QuestionItem({ item, courseTitle, onDone }: { item: LessonQuestion; courseTitle?: string; onDone: () => void }) {
  const [text, setText] = useState('')
  const reply = useMutation<LessonQuestion, ApiError, void>({
    mutationFn: () => answerQuestion(item.course_id, item.id, text.trim()),
    onSuccess: () => {
      setText('')
      onDone()
    },
  })
  const hide = useMutation({ mutationFn: () => hideQuestion(item.course_id, item.id), onSuccess: onDone })
  return (
    <li className="rounded-xl border border-slate-200 bg-panel p-4">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span className="font-semibold text-slate-800">{item.author_name}</span>
        <span>· {when(item.created_at)}</span>
        <span>· {courseTitle ? `${courseTitle} · ` : ''}{item.lesson_title}</span>
        {item.answered_by_instructor ? <Badge variant="success">Answered</Badge> : <Badge variant="warning">Waiting</Badge>}
      </div>
      <p className="mt-1.5 whitespace-pre-line text-sm text-slate-900">{item.body}</p>
      {item.answers.length > 0 && (
        <ul className="mt-2 space-y-1.5 border-l-2 border-slate-200 pl-3 text-sm">
          {item.answers.map((a) => (
            <li key={a.id}>
              <span className="text-xs font-semibold text-slate-600">{a.author_name} ({a.author_role}):</span>{' '}
              <span className="whitespace-pre-line text-slate-800">{a.body}</span>
            </li>
          ))}
        </ul>
      )}
      <div className="mt-3 space-y-2">
        <Textarea rows={2} placeholder="Write a clear, friendly answer" value={text} onChange={(e) => setText(e.target.value)} aria-label="Your answer" />
        <div className="flex items-center justify-between gap-2">
          <button type="button" className="text-xs text-slate-400 hover:text-red-600" onClick={() => hide.mutate()}>
            Hide question
          </button>
          <Button size="sm" leftIcon={<Send className="size-4" />} isLoading={reply.isPending} disabled={!text.trim()} onClick={() => reply.mutate()}>
            Send answer
          </Button>
        </div>
        {reply.isError && <p className="text-sm text-red-600">{reply.error.message}</p>}
      </div>
    </li>
  )
}

// =============================================================================
// Instructors (admin)
// =============================================================================

export function InstructorsPanel({ courseId, canManage }: { courseId: number; canManage: boolean }) {
  const queryClient = useQueryClient()
  const key = ['courses', 'admin', courseId, 'instructors']
  const q = useQuery({ queryKey: key, queryFn: () => listInstructors(courseId) })
  const [email, setEmail] = useState('')
  const add = useMutation<unknown, ApiError, void>({
    mutationFn: () => assignInstructor(courseId, email.trim()),
    onSuccess: () => {
      setEmail('')
      queryClient.invalidateQueries({ queryKey: key })
    },
  })
  const remove = useMutation({ mutationFn: (userId: number) => removeInstructor(courseId, userId), onSuccess: () => queryClient.invalidateQueries({ queryKey: key }) })
  return (
    <div className="space-y-5">
      {canManage && (
        <div className="rounded-xl border border-slate-200 bg-panel p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Add an instructor</h2>
          <p className="mt-1 text-sm text-slate-500">
            The instructor first registers a normal account. Enter that email here: the account becomes an instructor account and gets an email.
            Instructors can edit this course's lessons, videos, PDFs, quizzes and exam questions, answer students and see results — but not prices or publishing.
          </p>
          <form
            className="mt-3 flex flex-col gap-2 sm:flex-row"
            onSubmit={(e) => {
              e.preventDefault()
              if (email.trim()) add.mutate()
            }}
          >
            <Input type="email" placeholder="instructor@email.com" value={email} onChange={(e) => setEmail(e.target.value)} aria-label="Instructor email" className="flex-1" />
            <Button type="submit" leftIcon={<UserPlus className="size-4" />} isLoading={add.isPending} disabled={!email.trim()}>
              Assign
            </Button>
          </form>
          {add.isError && <p className="mt-2 text-sm text-red-600">{add.error.message}</p>}
        </div>
      )}
      {q.isLoading ? (
        <Skeleton className="h-20 rounded-xl" />
      ) : !q.data?.length ? (
        <EmptyState icon={Users} title="No instructors yet" description="Without an instructor, student questions go to the admins." />
      ) : (
        <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-panel">
          {q.data.map((i) => (
            <li key={i.user_id} className="flex items-center justify-between gap-3 p-4">
              <div>
                <p className="font-medium text-slate-900">{i.full_name}</p>
                <p className="text-xs text-slate-500">{i.email} · since {new Date(i.assigned_at).toLocaleDateString()}</p>
              </div>
              {canManage && (
                <Button size="sm" variant="outline" leftIcon={<Trash2 className="size-4" />} onClick={() => remove.mutate(i.user_id)}>
                  Remove
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
