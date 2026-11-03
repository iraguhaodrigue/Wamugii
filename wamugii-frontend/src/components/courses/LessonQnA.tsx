import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CornerDownRight, GraduationCap, MessageCircleQuestion, Send } from 'lucide-react'
import { askLessonQuestion, listLessonQuestions, replyAsStudent, type LessonQuestion } from '@/api/exams'
import type { ApiError } from '@/lib/apiClient'
import { Button, Skeleton, Textarea } from '@/components/ui'
import { cn } from '@/utils/cn'

function when(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

/**
 * Questions and answers under a lesson. Students ask; the course's instructors
 * are emailed and reply; classmates can help too. Instructor replies carry a
 * badge so the official answer is easy to spot.
 */
export function LessonQnA({ courseId, lessonId }: { courseId: number; lessonId: number }) {
  const queryClient = useQueryClient()
  const key = ['client', 'lesson-questions', courseId, lessonId]
  const query = useQuery({ queryKey: key, queryFn: () => listLessonQuestions(courseId, lessonId) })
  const [body, setBody] = useState('')
  const ask = useMutation<LessonQuestion, ApiError, string>({
    mutationFn: (text) => askLessonQuestion(courseId, lessonId, text),
    onSuccess: () => {
      setBody('')
      queryClient.invalidateQueries({ queryKey: key })
    },
  })

  return (
    <section className="rounded-2xl border border-slate-200 bg-panel p-4 sm:p-6" aria-labelledby={`qna-${lessonId}`}>
      <h3 id={`qna-${lessonId}`} className="flex items-center gap-2 text-base font-semibold text-slate-900">
        <MessageCircleQuestion className="size-5 text-brand-600" aria-hidden="true" /> Questions about this lesson
      </h3>
      <p className="mt-1 text-sm text-slate-500">Stuck? Ask here. Your instructor gets an email and answers you.</p>

      <form
        className="mt-4 space-y-2"
        onSubmit={(e) => {
          e.preventDefault()
          if (body.trim().length >= 3) ask.mutate(body.trim())
        }}
      >
        <Textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={3}
          maxLength={4000}
          placeholder="Write your question clearly. Say what you tried and where you got stuck."
          aria-label="Your question"
        />
        <div className="flex items-center justify-between gap-2">
          {ask.isError ? <p className="text-sm text-red-600">{ask.error.message}</p> : <span />}
          <Button type="submit" size="sm" leftIcon={<Send className="size-4" />} isLoading={ask.isPending} disabled={body.trim().length < 3}>
            Ask question
          </Button>
        </div>
      </form>

      <div className="mt-5 space-y-4">
        {query.isLoading ? (
          <Skeleton className="h-20 rounded-xl" />
        ) : (query.data ?? []).length === 0 ? (
          <p className="text-sm text-slate-500">No questions yet. Be the first to ask.</p>
        ) : (
          (query.data ?? []).map((q) => <Thread key={q.id} q={q} courseId={courseId} queryKey={key} />)
        )}
      </div>
    </section>
  )
}

function Thread({ q, courseId, queryKey }: { q: LessonQuestion; courseId: number; queryKey: unknown[] }) {
  const queryClient = useQueryClient()
  const [replying, setReplying] = useState(false)
  const [text, setText] = useState('')
  const reply = useMutation<LessonQuestion, ApiError, string>({
    mutationFn: (t) => replyAsStudent(courseId, q.id, t),
    onSuccess: () => {
      setText('')
      setReplying(false)
      queryClient.invalidateQueries({ queryKey })
    },
  })
  return (
    <article className="rounded-xl border border-slate-200 p-4">
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span className="font-semibold text-slate-700">{q.is_mine ? 'You' : q.author_name}</span>
        <span>· {when(q.created_at)}</span>
        {q.answered_by_instructor && (
          <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 font-semibold text-emerald-600">Answered</span>
        )}
      </div>
      <p className="mt-1.5 whitespace-pre-line text-sm text-slate-800">{q.body}</p>
      {q.answers.length > 0 && (
        <ul className="mt-3 space-y-2.5">
          {q.answers.map((a) => {
            const staff = a.author_role !== 'Student'
            return (
              <li key={a.id} className={cn('flex gap-2 rounded-lg p-3 text-sm', staff ? 'bg-brand-50' : 'bg-slate-50')}>
                <CornerDownRight className="mt-0.5 size-4 shrink-0 text-slate-400" aria-hidden="true" />
                <div className="min-w-0">
                  <p className="flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
                    <span className="font-semibold text-slate-700">{a.author_name}</span>
                    {staff && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-[var(--color-brand-solid)] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
                        <GraduationCap className="size-3" aria-hidden="true" /> {a.author_role}
                      </span>
                    )}
                    <span>· {when(a.created_at)}</span>
                  </p>
                  <p className="mt-1 whitespace-pre-line text-slate-800">{a.body}</p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
      {replying ? (
        <form
          className="mt-3 space-y-2"
          onSubmit={(e) => {
            e.preventDefault()
            if (text.trim()) reply.mutate(text.trim())
          }}
        >
          <Textarea value={text} onChange={(e) => setText(e.target.value)} rows={2} aria-label="Your reply" placeholder="Help a classmate or add details" />
          <div className="flex justify-end gap-2">
            <Button type="button" size="sm" variant="ghost" onClick={() => setReplying(false)}>Cancel</Button>
            <Button type="submit" size="sm" isLoading={reply.isPending} disabled={!text.trim()}>Reply</Button>
          </div>
        </form>
      ) : (
        <button type="button" onClick={() => setReplying(true)} className="mt-2 text-xs font-semibold text-brand-600 hover:text-brand-700">
          Reply
        </button>
      )}
    </article>
  )
}
