import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Award,
  CheckCircle2,
  Clock,
  Flag,
  Maximize,
  MonitorX,
  RotateCcw,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import { getPublicCourse } from '@/api/courses'
import {
  getExamOverview,
  reportExamEvent,
  saveExamAnswers,
  startExam,
  submitExam,
  type ExamAnswer,
  type ExamOverview,
  type ExamQuestionPublic,
  type ExamResult,
  type ExamSession,
} from '@/api/exams'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Button, ErrorState, Modal, Skeleton } from '@/components/ui'
import { useAppShellTheme } from '@/context/ThemeContext'
import {
  enterFullscreen,
  exitFullscreen,
  fullscreenSupported,
  LEAVE_REASONS,
  NOTICE_TEXT,
  useProctor,
} from '@/components/exam/useProctor'
import { cn } from '@/utils/cn'

/**
 * The final exam of a course, in the style of a proctored online exam.
 *
 * Intro (rules, attempts) -> running exam (full screen, timer, question map,
 * autosave) -> result. Leaving the exam screen is detected (useProctor), each
 * leave is reported to the server, and the server submits the attempt on the
 * last allowed leave -- the browser only shows what the server decided.
 */

const KIND_LABEL: Record<string, string> = {
  TRUE_FALSE: 'True or false',
  SINGLE: 'Single answer',
  MULTIPLE: 'Multiple answers',
  FILL_BLANK: 'Fill in the blank',
}
const KIND_HINT: Record<string, string> = {
  TRUE_FALSE: 'Is this statement true or false?',
  SINGLE: 'Choose the one best answer.',
  MULTIPLE: 'Choose ALL the correct answers. Every correct option must be chosen.',
  FILL_BLANK: 'Type the missing word or number.',
}
const REASON_TEXT: Record<string, string> = {
  STUDENT: 'You submitted the exam.',
  LEAVE_LIMIT: 'The exam was submitted automatically because you left the exam screen too many times.',
  TIME_UP: 'The time ran out, so the exam was submitted with the answers you had saved.',
}

function isAnswered(a: ExamAnswer | undefined): boolean {
  if (a === null || a === undefined) return false
  if (Array.isArray(a)) return a.length > 0
  if (typeof a === 'string') return a.trim().length > 0
  return true
}

function fmtClock(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

function ordinal(n: number): string {
  const tail = n % 100 >= 11 && n % 100 <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' } as Record<number, string>)[n % 10] ?? 'th'
  return `${n}${tail}`
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export function ClientCourseExam() {
  useAppShellTheme()
  const { slug } = useParams<{ slug: string }>()
  const queryClient = useQueryClient()
  const courseQuery = useQuery({ queryKey: ['courses', 'public-detail', slug], queryFn: () => getPublicCourse(slug!), enabled: Boolean(slug) })
  const course = courseQuery.data
  const overviewQuery = useQuery<ExamOverview, ApiError>({
    queryKey: ['client', 'exam', course?.id],
    queryFn: () => getExamOverview(course!.id),
    enabled: Boolean(course),
  })

  const [session, setSession] = useState<ExamSession | null>(null)
  const [result, setResult] = useState<ExamResult | null>(null)
  const [startError, setStartError] = useState<string | null>(null)
  const [starting, setStarting] = useState(false)

  const begin = useCallback(async () => {
    if (!course) return
    setStartError(null)
    setStarting(true)
    // Full screen must be requested inside the click.
    await enterFullscreen()
    try {
      const resumed = Boolean(overviewQuery.data?.in_progress_attempt_id)
      const s = await startExam(course.id)
      setSession(s)
      if (resumed) {
        // Coming back to an attempt that was open before (refresh, closed tab) counts as one leave.
        const r = await reportExamEvent(s.attempt_id, 'leave', 'page_reload')
        if (r.submitted && r.result) {
          await exitFullscreen()
          setSession(null)
          setResult(r.result)
        } else {
          setSession({ ...s, leave_count: r.leave_count })
        }
      }
    } catch (err) {
      await exitFullscreen()
      setStartError((err as ApiError).message ?? 'Could not start the exam.')
    } finally {
      setStarting(false)
    }
  }, [course, overviewQuery.data])

  const finished = useCallback(
    async (r: ExamResult) => {
      await exitFullscreen()
      setSession(null)
      setResult(r)
      queryClient.invalidateQueries({ queryKey: ['client', 'exam', course?.id] })
      queryClient.invalidateQueries({ queryKey: ['client', 'learning'] })
    },
    [course?.id, queryClient],
  )

  if (courseQuery.isLoading || (course && overviewQuery.isLoading)) {
    return (
      <ExamShell>
        <div className="mx-auto max-w-3xl space-y-4 p-6">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-64 rounded-2xl" />
        </div>
      </ExamShell>
    )
  }
  if (!course || overviewQuery.isError) {
    return (
      <ExamShell>
        <div className="mx-auto max-w-xl p-6">
          <ErrorState
            title="Couldn't open the exam"
            message={overviewQuery.error?.status === 404 ? 'You are not enrolled in this course.' : 'Please try again.'}
            onRetry={() => overviewQuery.refetch()}
          />
        </div>
      </ExamShell>
    )
  }

  if (session) return <ExamRunner session={session} onFinished={finished} />

  return (
    <ExamShell>
      {result ? (
        <ExamResultView result={result} slug={course.slug} courseTitle={course.title} onBack={() => setResult(null)} />
      ) : (
        <ExamIntro
          overview={overviewQuery.data!}
          courseTitle={course.title}
          slug={course.slug}
          starting={starting}
          error={startError}
          onStart={begin}
        />
      )}
    </ExamShell>
  )
}

function ExamShell({ children }: { children: React.ReactNode }) {
  return <div className="app-atmosphere min-h-svh">{children}</div>
}

// --- intro -------------------------------------------------------------------------

function ExamIntro({
  overview: ov,
  courseTitle,
  slug,
  starting,
  error,
  onStart,
}: {
  overview: ExamOverview
  courseTitle: string
  slug: string
  starting: boolean
  error: string | null
  onStart: () => void
}) {
  const [agreed, setAgreed] = useState(false)
  const resume = Boolean(ov.in_progress_attempt_id)
  const types = ov.type_counts ?? {}
  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:py-12">
      <Link to={paths.client.courseDetail(slug)} className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600">
        <ArrowLeft className="size-4" aria-hidden="true" /> Back to the course
      </Link>
      <p className="mt-6 text-xs font-bold uppercase tracking-wider text-brand-600">Final exam</p>
      <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{courseTitle}</h1>

      {!ov.available ? (
        <p className="mt-6 rounded-xl border border-slate-200 bg-panel p-5 text-slate-600">This course does not have a final exam yet.</p>
      ) : (
        <>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              ['Questions', String(ov.question_count)],
              ['Time', `${ov.minutes} min`],
              ['Pass mark', `${ov.pass_percent}%`],
              ['Attempts left', `${ov.attempts_left} of ${ov.max_attempts}`],
            ].map(([label, value]) => (
              <div key={label} className="rounded-xl border border-slate-200 bg-panel p-4 text-center">
                <p className="text-xl font-bold text-slate-900 sm:text-2xl">{value}</p>
                <p className="mt-0.5 text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            {Object.entries(types).filter(([, n]) => n > 0).map(([k, n]) => (
              <span key={k} className="rounded-full border border-slate-200 bg-panel px-3 py-1 font-medium text-slate-600">
                {n} × {KIND_LABEL[k] ?? k}
              </span>
            ))}
          </div>

          <div className="mt-6 rounded-2xl border border-amber-300/50 bg-amber-50 p-5">
            <h2 className="flex items-center gap-2 font-semibold text-amber-900">
              <ShieldCheck className="size-5" aria-hidden="true" /> Exam rules — read before you start
            </h2>
            <ul className="mt-3 space-y-2 text-sm leading-relaxed text-amber-900">
              <li>• The exam opens in <b>full screen</b>. Close other apps and turn off notifications first.</li>
              <li>• Do not switch tabs, open other apps or leave full screen. Each time you leave the exam screen you get a warning.</li>
              <li>• On the <b>{ordinal(ov.max_leaves)}</b> time you leave, the exam is <b>submitted automatically</b> with the answers you have given.</li>
              <li>• Copying, pasting, right-click and screenshots are turned off.</li>
              <li>• Your answers are saved as you go. If the page reloads, you can continue — but it counts as leaving the screen.</li>
              <li>• When the timer reaches 0:00 the exam is submitted for you.</li>
              <li>• Multiple-answer questions score only when you choose every correct option.</li>
            </ul>
          </div>

          {ov.attempts.length > 0 && (
            <div className="mt-6">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Your attempts</h2>
              <ul className="mt-2 divide-y divide-slate-200 rounded-xl border border-slate-200 bg-panel">
                {ov.attempts.map((a) => (
                  <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-sm">
                    <span className="text-slate-600">{fmtDate(a.started_at)}</span>
                    {a.status === 'IN_PROGRESS' ? (
                      <span className="font-semibold tone-amber">In progress</span>
                    ) : (
                      <span className={cn('font-semibold', a.passed ? 'tone-emerald' : 'text-red-600')}>
                        {a.percent}% · {a.passed ? 'Passed' : 'Not passed'}
                        {a.submit_reason && a.submit_reason !== 'STUDENT' && (
                          <span className="ml-1 font-normal text-slate-500">({a.submit_reason === 'TIME_UP' ? 'time up' : 'left the screen'})</span>
                        )}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-8 space-y-4">
            {ov.passed ? (
              <div className="flex flex-col items-start gap-3 rounded-2xl border border-emerald-300/50 bg-emerald-50 p-5 sm:flex-row sm:items-center sm:justify-between">
                <p className="flex items-center gap-2 font-semibold text-emerald-800">
                  <Award className="size-5" aria-hidden="true" /> You passed with {ov.best_percent}%. Your certificate is ready.
                </p>
                <Link to={`${paths.client.courseDetail(slug)}?certificate=1`} className="inline-flex h-10 items-center rounded-lg bg-emerald-700 px-4 text-sm font-semibold text-white hover:bg-emerald-800">
                  Get my certificate
                </Link>
              </div>
            ) : ov.eligible ? (
              <>
                {!resume && (
                  <label className="flex cursor-pointer items-start gap-3 text-sm text-slate-700">
                    <input type="checkbox" className="mt-0.5 size-4 accent-[var(--color-brand-solid)]" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />
                    I have read the rules. I will take the exam alone, without notes, other tabs or other people's help.
                  </label>
                )}
                <Button size="lg" leftIcon={<Maximize className="size-4" />} isLoading={starting} disabled={!resume && !agreed} onClick={onStart}>
                  {resume ? 'Continue my exam' : 'Start the exam in full screen'}
                </Button>
                {resume && <p className="text-sm text-amber-700">{ov.reason}</p>}
                {!fullscreenSupported() && (
                  <p className="text-xs text-slate-500">Your browser does not support full screen. Leaving this page or switching apps is still detected.</p>
                )}
              </>
            ) : (
              <p className="rounded-xl border border-slate-200 bg-panel p-4 text-sm text-slate-600">
                {ov.reason}
                {ov.next_attempt_at && <> Next attempt from <b>{fmtDate(ov.next_attempt_at)}</b>.</>}
              </p>
            )}
            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
          </div>
        </>
      )}
    </div>
  )
}

// --- runner ------------------------------------------------------------------------

function ExamRunner({ session, onFinished }: { session: ExamSession; onFinished: (r: ExamResult) => void }) {
  const questions = session.questions
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, ExamAnswer>>(() => ({ ...(session.answers as Record<string, ExamAnswer>) }))
  const [flags, setFlags] = useState<Set<number>>(new Set())
  const [leaves, setLeaves] = useState(session.leave_count)
  const [warning, setWarning] = useState<{ count: number; detail: string } | null>(null)
  const [toast, setToast] = useState<string | null>(null)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [saveState, setSaveState] = useState<'saved' | 'saving' | 'error'>('saved')
  const dirty = useRef<Record<string, ExamAnswer>>({})
  const done = useRef(false)

  // Clock: offset the local clock by the server's, so a wrong phone clock doesn't matter.
  const offset = useMemo(() => new Date(session.server_now).getTime() - Date.now(), [session.server_now])
  const deadline = new Date(session.deadline_at).getTime()
  const [remaining, setRemaining] = useState(() => deadline - (Date.now() + offset))

  const finish = useCallback(
    async (r: ExamResult) => {
      if (done.current) return
      done.current = true
      onFinished(r)
    },
    [onFinished],
  )

  const doSubmit = useCallback(async () => {
    if (done.current) return
    setSubmitting(true)
    try {
      const r = await submitExam(session.attempt_id, answers)
      await finish(r)
    } catch (err) {
      setSubmitting(false)
      setToast((err as ApiError).message ?? 'Could not submit. Check your connection and try again.')
    }
  }, [answers, finish, session.attempt_id])

  const onLeave = useCallback(
    async (detail: string) => {
      if (done.current) return
      try {
        const r = await reportExamEvent(session.attempt_id, 'leave', detail)
        setLeaves(r.leave_count)
        if (r.submitted && r.result) {
          await finish(r.result)
          return
        }
        setWarning({ count: r.leave_count, detail })
      } catch {
        setWarning({ count: leaves + 1, detail })
      }
    },
    [finish, leaves, session.attempt_id],
  )
  const onNotice = useCallback(
    (detail: string) => {
      setToast(NOTICE_TEXT[detail] ?? 'That action is turned off during the exam.')
      reportExamEvent(session.attempt_id, 'notice', detail).catch(() => undefined)
    },
    [session.attempt_id],
  )
  const proctor = useProctor({ active: !done.current, onLeave, onNotice })

  // Timer
  useEffect(() => {
    const t = window.setInterval(() => {
      const left = deadline - (Date.now() + offset)
      setRemaining(left)
      if (left <= 0) {
        window.clearInterval(t)
        doSubmit()
      }
    }, 500)
    return () => window.clearInterval(t)
  }, [deadline, offset, doSubmit])
  const warnedAt = useRef<Set<number>>(new Set())
  useEffect(() => {
    for (const min of [10, 5, 1]) {
      if (remaining <= min * 60_000 && remaining > (min - 0.5) * 60_000 && !warnedAt.current.has(min)) {
        warnedAt.current.add(min)
        setToast(`${min} minute${min > 1 ? 's' : ''} left. Check your answers.`)
      }
    }
  }, [remaining])

  // Autosave changed answers
  useEffect(() => {
    const t = window.setInterval(async () => {
      const batch = dirty.current
      if (Object.keys(batch).length === 0 || done.current) return
      dirty.current = {}
      setSaveState('saving')
      try {
        await saveExamAnswers(session.attempt_id, batch)
        setSaveState('saved')
      } catch {
        dirty.current = { ...batch, ...dirty.current }
        setSaveState('error')
      }
    }, 2000)
    return () => window.clearInterval(t)
  }, [session.attempt_id])

  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(() => setToast(null), 3500)
    return () => window.clearTimeout(t)
  }, [toast])

  const setAnswer = (qid: number, value: ExamAnswer) => {
    setAnswers((prev) => ({ ...prev, [String(qid)]: value }))
    dirty.current[String(qid)] = value
    setSaveState('saving')
  }

  const q = questions[index]!
  const answeredCount = questions.filter((x) => isAnswered(answers[String(x.id)])).length
  const unanswered = questions.length - answeredCount
  const low = remaining < 5 * 60_000
  const leavesLeft = session.max_leaves - leaves

  const sections = useMemo(() => {
    const out: { kind: string; items: { q: ExamQuestionPublic; i: number }[] }[] = []
    questions.forEach((x, i) => {
      const last = out[out.length - 1]
      if (last && last.kind === x.kind) last.items.push({ q: x, i })
      else out.push({ kind: x.kind, items: [{ q: x, i }] })
    })
    return out
  }, [questions])

  return (
    <div className="app-atmosphere flex min-h-svh select-none flex-col" onCopy={(e) => e.preventDefault()}>
      {/* top bar */}
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-panel/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-3 py-2.5 sm:px-5">
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-slate-900">{session.course_title} — Final exam</p>
            <p className="text-[11px] text-slate-500">
              {answeredCount}/{questions.length} answered ·{' '}
              <span className={cn(saveState === 'error' && 'text-red-600')}>
                {saveState === 'saving' ? 'saving…' : saveState === 'error' ? 'not saved — check connection' : 'all answers saved'}
              </span>
            </p>
          </div>
          <span
            className={cn(
              'hidden items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold sm:inline-flex',
              leaves === 0 ? 'bg-emerald-500/10 tone-emerald' : 'bg-red-500/10 text-red-600',
            )}
            title="Times you left the exam screen"
          >
            <MonitorX className="size-3.5" aria-hidden="true" /> Leaves {leaves}/{session.max_leaves}
          </span>
          <span
            className={cn(
              'inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-mono text-base font-bold tabular-nums',
              low ? 'animate-pulse bg-red-600 text-white' : 'bg-slate-100 text-slate-900',
            )}
            aria-label="Time remaining"
          >
            <Clock className="size-4" aria-hidden="true" /> {fmtClock(remaining)}
          </span>
          <Button size="sm" onClick={() => setConfirmOpen(true)} disabled={submitting}>
            Submit
          </Button>
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-6xl flex-1 gap-5 px-3 py-5 sm:px-5 lg:grid-cols-[1fr_17rem]">
        {/* question */}
        <main className="min-w-0">
          <div className="rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] sm:p-7">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs font-bold uppercase tracking-wider text-brand-600">
                Question {index + 1} of {questions.length} · {KIND_LABEL[q.kind]}
              </p>
              <button
                type="button"
                onClick={() =>
                  setFlags((prev) => {
                    const next = new Set(prev)
                    if (next.has(q.id)) next.delete(q.id)
                    else next.add(q.id)
                    return next
                  })
                }
                className={cn(
                  'inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-xs font-semibold',
                  flags.has(q.id) ? 'border-amber-400 bg-amber-50 text-amber-700' : 'border-slate-200 text-slate-500 hover:text-slate-700',
                )}
              >
                <Flag className="size-3.5" aria-hidden="true" /> {flags.has(q.id) ? 'Flagged' : 'Flag for review'}
              </button>
            </div>
            <p className="mt-1 text-sm text-slate-500">{KIND_HINT[q.kind]}</p>
            <QuestionBody q={q} value={answers[String(q.id)]} onChange={(v) => setAnswer(q.id, v)} />
          </div>

          <div className="mt-4 flex items-center justify-between gap-3">
            <Button variant="outline" leftIcon={<ArrowLeft className="size-4" />} disabled={index === 0} onClick={() => setIndex((i) => i - 1)}>
              Previous
            </Button>
            {index < questions.length - 1 ? (
              <Button onClick={() => setIndex((i) => i + 1)}>
                Next <ArrowRight className="size-4" aria-hidden="true" />
              </Button>
            ) : (
              <Button onClick={() => setConfirmOpen(true)}>Review & submit</Button>
            )}
          </div>
        </main>

        {/* question map */}
        <aside className="rounded-2xl border border-slate-200 bg-panel p-4 lg:sticky lg:top-20 lg:self-start">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Question map</p>
          <div className="mt-3 space-y-3">
            {sections.map((sec) => (
              <div key={sec.kind}>
                <p className="mb-1.5 text-[11px] font-semibold text-slate-400">{KIND_LABEL[sec.kind]}</p>
                <div className="flex flex-wrap gap-1.5">
                  {sec.items.map(({ q: x, i }) => {
                    const done = isAnswered(answers[String(x.id)])
                    return (
                      <button
                        key={x.id}
                        type="button"
                        onClick={() => setIndex(i)}
                        aria-label={`Question ${i + 1}${done ? ', answered' : ''}${flags.has(x.id) ? ', flagged' : ''}`}
                        className={cn(
                          'relative flex size-8 items-center justify-center rounded-md text-xs font-semibold transition-colors',
                          i === index && 'ring-2 ring-brand-500 ring-offset-1 ring-offset-[var(--color-bg)]',
                          done ? 'bg-[var(--color-brand-solid)] text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
                        )}
                      >
                        {i + 1}
                        {flags.has(x.id) && <span className="absolute -right-0.5 -top-0.5 size-2.5 rounded-full bg-amber-400" />}
                      </button>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 space-y-1 text-[11px] text-slate-500">
            <p className="flex items-center gap-2"><span className="size-3 rounded bg-[var(--color-brand-solid)]" /> Answered</p>
            <p className="flex items-center gap-2"><span className="size-3 rounded bg-slate-200" /> Not answered</p>
            <p className="flex items-center gap-2"><span className="size-2.5 rounded-full bg-amber-400" /> Flagged</p>
          </div>
        </aside>
      </div>

      {/* leave warning */}
      <Modal isOpen={Boolean(warning) || (proctor.away && !warning)} onClose={() => undefined} title="You left the exam screen" size="sm">
        <div className="space-y-3 text-sm">
          <div className="flex items-start gap-3 rounded-xl bg-red-500/10 p-3 text-red-700">
            <AlertTriangle className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
            <div>
              <p className="font-semibold">Warning {warning?.count ?? leaves} of {session.max_leaves}</p>
              <p className="mt-0.5">{LEAVE_REASONS[warning?.detail ?? ''] ?? 'You left the exam screen.'}</p>
            </div>
          </div>
          <p className="text-slate-600">
            {leavesLeft <= 1
              ? 'This is your last warning. If you leave the exam screen again, your exam will be submitted automatically.'
              : `If you leave the exam screen ${leavesLeft} more times, your exam will be submitted automatically.`}
          </p>
          <Button
            className="w-full"
            leftIcon={<Maximize className="size-4" />}
            onClick={async () => {
              await proctor.acknowledge()
              setWarning(null)
            }}
          >
            Return to the exam
          </Button>
        </div>
      </Modal>

      {/* not in full screen (e.g. Esc pressed before the warning shows) */}
      {fullscreenSupported() && !proctor.isFullscreen && !proctor.away && !warning && !confirmOpen && (
        <div className="fixed inset-x-0 bottom-0 z-40 flex items-center justify-center gap-3 bg-red-600 px-4 py-3 text-sm text-white">
          <AlertTriangle className="size-4" aria-hidden="true" /> The exam must stay in full screen.
          <button type="button" className="rounded-md bg-white/20 px-3 py-1 font-semibold" onClick={() => enterFullscreen()}>
            Go full screen
          </button>
        </div>
      )}

      {/* submit confirm */}
      <Modal isOpen={confirmOpen} onClose={() => setConfirmOpen(false)} title="Submit your exam?" size="sm">
        <div className="space-y-3 text-sm text-slate-600">
          <p>
            You answered <b className="text-slate-900">{answeredCount}</b> of {questions.length} questions.
            {unanswered > 0 && <> <b className="text-red-600">{unanswered} unanswered</b> question{unanswered > 1 ? 's count' : ' counts'} as wrong.</>}
          </p>
          {flags.size > 0 && <p>You flagged {flags.size} question{flags.size > 1 ? 's' : ''} for review.</p>}
          <p>After you submit, you cannot change your answers.</p>
          <div className="flex gap-2 pt-1">
            <Button variant="outline" className="flex-1" onClick={() => setConfirmOpen(false)}>Keep working</Button>
            <Button
              className="flex-1"
              isLoading={submitting}
              onClick={() => {
                proctor.pause(5000)
                doSubmit()
              }}
            >
              Submit now
            </Button>
          </div>
        </div>
      </Modal>

      {toast && (
        <div role="status" className="fixed bottom-16 left-1/2 z-50 -translate-x-1/2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-lg">
          {toast}
        </div>
      )}
    </div>
  )
}

function QuestionBody({ q, value, onChange }: { q: ExamQuestionPublic; value: ExamAnswer | undefined; onChange: (v: ExamAnswer) => void }) {
  if (q.kind === 'FILL_BLANK') {
    const parts = q.question.split(/_{3,}/)
    return (
      <div className="mt-5 text-lg leading-loose text-slate-900">
        {parts.map((part, i) => (
          <span key={i}>
            {part}
            {i < parts.length - 1 && (
              <input
                type="text"
                autoComplete="off"
                spellCheck={false}
                value={typeof value === 'string' ? value : ''}
                onChange={(e) => onChange(e.target.value)}
                aria-label="Your answer"
                className="mx-1 inline-block w-40 select-text rounded-md border-b-2 border-brand-500 bg-brand-50/60 px-2 py-0.5 text-center text-base font-semibold text-brand-700 outline-none focus:bg-brand-50 sm:w-52"
                placeholder="type here"
              />
            )}
          </span>
        ))}
      </div>
    )
  }

  const multiple = q.kind === 'MULTIPLE'
  const chosen = new Set<number>(Array.isArray(value) ? value : typeof value === 'number' ? [value] : [])
  return (
    <div className="mt-4">
      <p className="text-lg font-medium leading-relaxed text-slate-900">{q.question}</p>
      <div className={cn('mt-5 grid gap-2.5', q.kind === 'TRUE_FALSE' && 'sm:grid-cols-2')}>
        {q.options.map((o, i) => {
          const on = chosen.has(o.id)
          return (
            <button
              key={o.id}
              type="button"
              role={multiple ? 'checkbox' : 'radio'}
              aria-checked={on}
              onClick={() => {
                if (multiple) {
                  const next = new Set(chosen)
                  if (on) next.delete(o.id)
                  else next.add(o.id)
                  onChange([...next].sort((a, b) => a - b))
                } else {
                  onChange(o.id)
                }
              }}
              className={cn(
                'flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left text-[15px] transition-colors',
                on ? 'border-brand-500 bg-brand-50 text-slate-900 ring-1 ring-brand-500' : 'border-slate-200 text-slate-700 hover:border-brand-300 hover:bg-slate-50',
              )}
            >
              <span
                className={cn(
                  'flex size-6 shrink-0 items-center justify-center border text-xs font-bold',
                  multiple ? 'rounded-md' : 'rounded-full',
                  on ? 'border-brand-600 bg-[var(--color-brand-solid)] text-white' : 'border-slate-300 text-slate-500',
                )}
              >
                {on ? '✓' : q.kind === 'TRUE_FALSE' ? (i === 0 ? 'T' : 'F') : String.fromCharCode(65 + i)}
              </span>
              <span className="flex-1">{o.text}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

// --- result -----------------------------------------------------------------------------

function ExamResultView({ result: r, slug, courseTitle, onBack }: { result: ExamResult; slug: string; courseTitle: string; onBack: () => void }) {
  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:py-14">
      <div className="hero-in rounded-3xl border border-slate-200 bg-panel p-6 text-center shadow-[var(--shadow-card)] sm:p-10">
        {r.passed ? (
          <CheckCircle2 className="mx-auto size-14 text-emerald-500" aria-hidden="true" />
        ) : (
          <XCircle className="mx-auto size-14 text-red-500" aria-hidden="true" />
        )}
        <p className="mt-3 text-xs font-bold uppercase tracking-wider text-brand-600">{courseTitle} — Final exam</p>
        <h1 className="mt-1 text-3xl font-extrabold text-slate-900">{r.passed ? 'Congratulations, you passed!' : 'Not passed this time'}</h1>
        <p className="mt-4 text-5xl font-black tabular-nums text-slate-900">{r.percent}%</p>
        <p className="mt-1 text-sm text-slate-500">
          {r.score} of {r.total} correct · pass mark {r.pass_percent}%
        </p>
        <p className="mt-3 text-sm text-slate-600">{REASON_TEXT[r.submit_reason] ?? ''}</p>

        {r.topic_scores.length > 0 && (
          <div className="mt-6 space-y-2.5 text-left">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Score by topic</p>
            {r.topic_scores.map((t) => {
              const pct = t.total ? Math.round((100 * t.correct) / t.total) : 0
              return (
                <div key={t.topic}>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-700">{t.topic}</span>
                    <span className="font-semibold text-slate-900">{t.correct}/{t.total}</span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div className={cn('h-full rounded-full', pct >= r.pass_percent ? 'bg-emerald-500' : 'bg-amber-500')} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        )}

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          {r.certificate_ready ? (
            <Link to={`${paths.client.courseDetail(slug)}?certificate=1`} className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-emerald-700 px-5 text-sm font-semibold text-white hover:bg-emerald-800">
              <Award className="size-4" aria-hidden="true" /> Get my certificate
            </Link>
          ) : (
            <>
              <Link to={paths.client.courseDetail(slug)} className="inline-flex h-11 items-center justify-center gap-2 rounded-lg border border-slate-300 px-5 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                Review the lessons
              </Link>
              {r.attempts_left > 0 && (
                <Button variant="outline" leftIcon={<RotateCcw className="size-4" />} onClick={onBack}>
                  {r.next_attempt_at ? `Next attempt from ${fmtDate(r.next_attempt_at)}` : `Try again (${r.attempts_left} left)`}
                </Button>
              )}
            </>
          )}
        </div>
        {!r.passed && r.attempts_left === 0 && (
          <p className="mt-4 text-sm text-slate-500">You have used all your attempts. Ask your instructor for another attempt.</p>
        )}
      </div>
    </div>
  )
}
