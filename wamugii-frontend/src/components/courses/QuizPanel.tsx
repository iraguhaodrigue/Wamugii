import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Award, CheckCircle2, ClipboardCheck, RotateCcw, XCircle } from 'lucide-react'
import { getLessonQuiz, submitLessonQuiz, type Quiz, type QuizResult } from '@/api/courses'
import type { ApiError } from '@/lib/apiClient'
import { Button, Skeleton } from '@/components/ui'
import { cn } from '@/utils/cn'

/**
 * The quiz at the end of a lesson.
 *
 * Questions arrive without answers; the student picks one option per
 * question and submits. Marking happens on the server, which returns the
 * correct option and an explanation for each question -- shown inline in
 * green/red. Passing (70%+) also completes the lesson, so the player's
 * progress and sidebar ticks refresh straight away. Unlimited retries.
 */
export function QuizPanel({
  courseId,
  lessonId,
  onPassed,
}: {
  courseId: number
  lessonId: number
  /** Called after a passing submission (e.g. to offer "Next lesson"). */
  onPassed?: () => void
}) {
  const queryClient = useQueryClient()
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [result, setResult] = useState<QuizResult | null>(null)

  const quizQuery = useQuery<Quiz, ApiError>({
    queryKey: ['client', 'quiz', courseId, lessonId],
    queryFn: () => getLessonQuiz(courseId, lessonId),
  })

  const submit = useMutation<QuizResult, ApiError, Record<number, number>>({
    mutationFn: (a) => submitLessonQuiz(courseId, lessonId, a),
    onSuccess: (res) => {
      setResult(res)
      queryClient.invalidateQueries({ queryKey: ['client', 'learning'] })
      queryClient.invalidateQueries({ queryKey: ['client', 'progress', courseId] })
      queryClient.invalidateQueries({ queryKey: ['client', 'quiz', courseId, lessonId] })
      if (res.passed) onPassed?.()
    },
  })

  if (quizQuery.isLoading) return <Skeleton className="h-48 rounded-2xl" />
  const quiz = quizQuery.data
  if (!quiz || quiz.questions.length === 0) return null

  const answeredAll = quiz.questions.every((q) => answers[q.id] !== undefined)
  const byId = new Map(result?.results.map((r) => [r.question_id, r]))

  function retry() {
    setAnswers({})
    setResult(null)
  }

  return (
    <section className="rounded-2xl border border-brand-400/30 bg-panel p-6 shadow-[var(--shadow-glow-brand)]" id="lesson-quiz">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white">
            <ClipboardCheck className="size-5" aria-hidden="true" />
          </span>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Check your understanding</h3>
            <p className="text-sm text-slate-500">
              {quiz.questions.length} questions · pass mark {quiz.pass_percent}% · passing completes this lesson
            </p>
          </div>
        </div>
        {quiz.passed && !result && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-3 py-1 text-sm font-semibold text-emerald-600">
            <CheckCircle2 className="size-4" aria-hidden="true" />
            Passed · best {quiz.best_score}/{quiz.best_total}
          </span>
        )}
      </div>

      <ol className="mt-6 space-y-6">
        {quiz.questions.map((q, qi) => {
          const marked = byId.get(q.id)
          return (
            <li key={q.id}>
              <p className="font-medium text-slate-900">
                <span className="mr-2 text-brand-600">{qi + 1}.</span>
                {q.question}
              </p>
              <div className="mt-3 grid gap-2" role="radiogroup" aria-label={`Question ${qi + 1}`}>
                {q.options.map((option, oi) => {
                  const chosen = answers[q.id] === oi
                  const isCorrect = marked && marked.correct_index === oi
                  const isWrongPick = marked && chosen && !marked.is_correct
                  return (
                    <button
                      key={oi}
                      type="button"
                      role="radio"
                      aria-checked={chosen}
                      disabled={Boolean(result)}
                      onClick={() => setAnswers((a) => ({ ...a, [q.id]: oi }))}
                      className={cn(
                        'flex items-start gap-3 rounded-xl border px-4 py-3 text-left text-sm transition-all duration-200',
                        !marked && chosen && 'border-brand-400 bg-brand-50 text-slate-900 ring-1 ring-brand-400/50',
                        !marked && !chosen && 'border-slate-200 text-slate-700 hover:-translate-y-0.5 hover:border-brand-400/50',
                        isCorrect && 'border-emerald-400 bg-emerald-500/10 text-slate-900',
                        isWrongPick && 'border-red-400 bg-red-500/10 text-slate-900',
                        marked && !isCorrect && !isWrongPick && 'border-slate-200 text-slate-500 opacity-70',
                      )}
                    >
                      <span
                        className={cn(
                          'mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border text-[11px] font-bold',
                          chosen ? 'border-brand-500 bg-brand-500 text-white' : 'border-slate-300 text-slate-400',
                          isCorrect && 'border-emerald-500 bg-emerald-500 text-white',
                          isWrongPick && 'border-red-500 bg-red-500 text-white',
                        )}
                      >
                        {String.fromCharCode(65 + oi)}
                      </span>
                      <span className="flex-1">{option}</span>
                      {isCorrect && <CheckCircle2 className="chip-pop size-4 shrink-0 text-emerald-500" aria-label="Correct answer" />}
                      {isWrongPick && <XCircle className="chip-pop size-4 shrink-0 text-red-500" aria-label="Your answer" />}
                    </button>
                  )
                })}
              </div>
              {marked && marked.explanation && (
                <p className="price-swap mt-2 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600">
                  <span className="font-semibold text-slate-900">{marked.is_correct ? 'Correct. ' : 'Not quite. '}</span>
                  {marked.explanation}
                </p>
              )}
            </li>
          )
        })}
      </ol>

      {submit.isError && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {submit.error.message}
        </p>
      )}

      {result ? (
        <div
          className={cn(
            'price-swap mt-6 flex flex-wrap items-center justify-between gap-4 rounded-xl p-4',
            result.passed ? 'bg-emerald-500/10' : 'bg-amber-500/10',
          )}
        >
          <div className="flex items-center gap-3">
            {result.passed ? (
              <Award className="chip-pop size-8 text-emerald-500" aria-hidden="true" />
            ) : (
              <RotateCcw className="size-7 text-amber-500" aria-hidden="true" />
            )}
            <div>
              <p className="text-lg font-bold text-slate-900">
                {result.score}/{result.total} · {result.percent}%
              </p>
              <p className="text-sm text-slate-600">
                {result.passed
                  ? 'Well done — lesson complete!'
                  : `You need ${quiz.pass_percent}% to pass. Read the explanations, then try again.`}
              </p>
            </div>
          </div>
          <Button variant="outline" onClick={retry} leftIcon={<RotateCcw className="size-4" />}>
            Try again
          </Button>
        </div>
      ) : (
        <div className="mt-6 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-500">
            {Object.keys(answers).length}/{quiz.questions.length} answered
            {quiz.attempts > 0 && ` · ${quiz.attempts} earlier attempt${quiz.attempts === 1 ? '' : 's'}`}
          </p>
          <Button
            disabled={!answeredAll}
            isLoading={submit.isPending}
            onClick={() => submit.mutate(answers)}
            leftIcon={<ClipboardCheck className="size-4" />}
          >
            Submit answers
          </Button>
        </div>
      )}
    </section>
  )
}
