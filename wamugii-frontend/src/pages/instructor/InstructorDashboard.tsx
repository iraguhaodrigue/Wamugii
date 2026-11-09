import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, ClipboardCheck, GraduationCap, MessageCircleQuestion, Users } from 'lucide-react'
import { listMyTeachingCourses } from '@/api/exams'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import { Badge, EmptyState, ErrorState, Skeleton } from '@/components/ui'

/** An instructor's home: the courses an admin assigned to them. */
export function InstructorDashboard() {
  usePageTitle('My courses')
  const { user } = useAuth()
  const q = useQuery({ queryKey: ['instructor', 'courses'], queryFn: listMyTeachingCourses })
  const waiting = (q.data ?? []).reduce((n, c) => n + c.unanswered_questions, 0)

  return (
    <div className="space-y-6">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] p-6 text-white sm:p-8">
        <GraduationCap className="absolute -right-4 -top-4 size-36 opacity-15" aria-hidden="true" />
        <p className="text-sm font-semibold uppercase tracking-wider text-white/80">Instructor area</p>
        <h1 className="mt-1 text-2xl font-extrabold sm:text-3xl">Welcome, {user?.full_name?.split(' ')[0] ?? 'instructor'}</h1>
        <p className="mt-2 max-w-xl text-white/85">
          Keep your lessons up to date, answer your students and follow their results. Every question you answer helps a student finish.
        </p>
        {waiting > 0 && (
          <Link to={paths.instructor.questions} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-white/20 px-4 py-2 text-sm font-semibold backdrop-blur hover:bg-white/30">
            <MessageCircleQuestion className="size-4" aria-hidden="true" /> {waiting} question{waiting === 1 ? '' : 's'} waiting for you
          </Link>
        )}
      </div>

      {q.isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-40 rounded-2xl" />
          <Skeleton className="h-40 rounded-2xl" />
        </div>
      ) : q.isError ? (
        <ErrorState title="Couldn't load your courses" message="Please try again." onRetry={() => q.refetch()} />
      ) : !q.data?.length ? (
        <EmptyState icon={BookOpen} title="No courses yet" description="An administrator will assign courses to you. You'll get an email when they do." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {q.data.map((c) => (
            <Link
              key={c.id}
              to={paths.instructor.courseDetail(c.id)}
              className="group rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] transition-all hover:-translate-y-0.5 hover:border-brand-400 hover:shadow-[var(--shadow-glow-brand)]"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="text-lg font-bold text-slate-900 group-hover:text-brand-600">{c.title}</h2>
                <Badge variant={c.status === 'PUBLISHED' ? 'success' : 'neutral'}>{c.status}</Badge>
              </div>
              <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <Stat icon={BookOpen} label="Lessons" value={c.lesson_count} />
                <Stat icon={Users} label="Students" value={c.student_count} />
                <Stat icon={MessageCircleQuestion} label="Waiting questions" value={c.unanswered_questions} highlight={c.unanswered_questions > 0} />
                <Stat icon={ClipboardCheck} label="Exam questions" value={c.exam_question_count} />
              </dl>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

function Stat({ icon: Icon, label, value, highlight }: { icon: typeof BookOpen; label: string; value: number; highlight?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <Icon className={highlight ? 'size-4 text-amber-500' : 'size-4 text-slate-400'} aria-hidden="true" />
      <span className="text-slate-500">{label}</span>
      <span className={highlight ? 'ml-auto font-bold tone-amber' : 'ml-auto font-semibold text-slate-900'}>{value}</span>
    </div>
  )
}
