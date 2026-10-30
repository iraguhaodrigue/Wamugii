import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  Award,
  BookOpen,
  CheckCircle2,
  Clock,
  GraduationCap,
  Lock,
  PlayCircle,
  SearchX,
  Signal,
} from 'lucide-react'
import {
  enrollInCourse,
  getPublicCourse,
  type CoursePublicDetail,
  type EnrollResponse,
} from '@/api/courses'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Button, Container, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatMoney } from '@/utils/format'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'
import { NeuralArt } from '@/components/courses/NeuralArt'
import { getShowcase } from '@/components/courses/courseShowcase'

function formatDuration(minutes: number): string {
  if (minutes < 75) return minutes < 50 ? `${minutes} minutes` : 'About 1 hour'
  return `About ${Math.round(minutes / 30) / 2} hours`
}

export function CourseDetail() {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const { user, isAuthenticated } = useAuth()
  const [enrollError, setEnrollError] = useState<string | null>(null)

  const {
    data: course,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<CoursePublicDetail, ApiError>({
    queryKey: ['courses', 'public-detail', slug],
    queryFn: () => getPublicCourse(slug!),
    enabled: Boolean(slug),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const enrollMutation = useMutation<EnrollResponse, ApiError, number>({
    mutationFn: (courseId) => enrollInCourse(courseId),
    onSuccess: (resp) => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setEnrollError(null)
      // Free -> straight into the player. Pending payment -> their invoice page
      // so they can act on it.
      if (resp.enrollment.status === 'ACTIVE') {
        navigate(paths.client.courseDetail(resp.enrollment.course_slug))
      } else if (resp.enrollment.invoice_id) {
        navigate(paths.client.invoiceDetail(resp.enrollment.invoice_id))
      } else {
        navigate(paths.client.learning)
      }
    },
    onError: (err) => setEnrollError(err.message),
  })

  function handleEnroll() {
    if (!course) return
    if (!isAuthenticated) {
      // Preserve where we are so a successful login brings them back here.
      navigate(paths.login, { state: { from: location } })
      return
    }
    if (user?.role !== 'CLIENT') {
      setEnrollError(
        'Only client accounts can enroll. Please sign in with a client account to continue.',
      )
      return
    }
    enrollMutation.mutate(course.id)
  }

  if (isLoading) {
    return (
      <Container className="py-16 sm:py-20">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="mt-6 h-10 w-2/3" />
        <Skeleton className="mt-4 h-64 rounded-xl" />
      </Container>
    )
  }

  if (isError && error.status === 404) {
    return (
      <Container className="py-16 sm:py-20">
        <EmptyState
          icon={SearchX}
          title="Course not found"
          description="This course doesn't exist or isn't published."
          action={
            <Link
              to={paths.courses}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              <ArrowLeft className="size-4" aria-hidden="true" />
              Back to Courses
            </Link>
          }
        />
      </Container>
    )
  }

  if (isError || !course) {
    return (
      <Container className="py-16 sm:py-20">
        <ErrorState
          title="Couldn't load this course"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      </Container>
    )
  }

  const price = course.is_free ? null : formatMoney(course.price)
  const showcase = getShowcase(course.slug)
  const lessonCount = course.lessons.length || course.lesson_count
  const totalMinutes = showcase
    ? showcase.lessons.reduce((sum, l) => sum + l.minutes, 0)
    : lessonCount * 10
  const words = course.title.trim().split(/\s+/)
  const lastWord = words.pop()
  const [firstParagraph, ...moreParagraphs] = course.description.split(/\n\s*\n/)

  const stats = [
    { icon: BookOpen, label: `${lessonCount} lessons` },
    { icon: Clock, label: formatDuration(totalMinutes) },
    { icon: Signal, label: showcase?.level ?? 'Self-paced' },
    { icon: Award, label: 'Certificate' },
  ]

  const enrollButton = (dark: boolean) => (
    <Button
      className={dark ? 'w-full sm:w-auto shadow-[var(--shadow-glow-brand)]' : 'w-full'}
      size="lg"
      onClick={handleEnroll}
      isLoading={enrollMutation.isPending}
      leftIcon={<PlayCircle className="size-5" />}
    >
      {course.is_free ? 'Enroll free — start learning' : 'Enroll and generate invoice'}
    </Button>
  )

  return (
    <>
      {/* Animated hero */}
      <section className="relative overflow-hidden bg-[var(--color-brand-950)]">
        <div
          className="pointer-events-none absolute inset-0 bg-cover bg-top bg-no-repeat opacity-50"
          style={{ backgroundImage: "url('/graphics/gradient-blobs.svg')" }}
          aria-hidden="true"
        />
        <AnimatedTechBackground intensity="medium" />
        <Container className="relative py-14 sm:py-20">
          <Link
            to={paths.courses}
            className="hero-in inline-flex items-center gap-1.5 text-sm font-medium text-slate-400 hover:text-cyan-300"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            All courses
          </Link>
          <div className="mt-6 grid items-center gap-10 lg:grid-cols-2">
            <div>
              <div className="hero-in flex flex-wrap gap-2" style={{ animationDelay: '60ms' }}>
                {course.category && (
                  <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-cyan-300">
                    {course.category}
                  </span>
                )}
                <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-xs font-semibold text-emerald-300">
                  {course.is_free ? 'Free' : (price ?? 'Paid')}
                </span>
              </div>
              <h1
                className="hero-in mt-5 text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl lg:text-6xl"
                style={{ animationDelay: '120ms' }}
              >
                {words.join(' ')} <span className="text-gradient-hero">{lastWord}</span>
              </h1>
              <p className="hero-in mt-5 max-w-xl text-base text-white/75 sm:text-lg" style={{ animationDelay: '200ms' }}>
                {showcase?.tagline ?? firstParagraph}
              </p>
              <ul className="hero-in mt-7 flex flex-wrap gap-2.5" style={{ animationDelay: '280ms' }}>
                {stats.map(({ icon: Icon, label }) => (
                  <li
                    key={label}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/85 backdrop-blur-sm"
                  >
                    <Icon className="size-4 text-cyan-300" aria-hidden="true" />
                    {label}
                  </li>
                ))}
              </ul>
              <div className="hero-in mt-8" style={{ animationDelay: '360ms' }}>
                {enrollButton(true)}
                {enrollError && (
                  <p role="alert" className="mt-3 max-w-md rounded-lg bg-red-500/15 px-3 py-2 text-sm text-red-200">
                    {enrollError}
                  </p>
                )}
                {!isAuthenticated && (
                  <p className="mt-3 text-xs text-slate-400">You'll be asked to sign in first.</p>
                )}
              </div>
            </div>
            <div className="hero-in mx-auto w-full max-w-md lg:max-w-lg" style={{ animationDelay: '300ms' }}>
              <NeuralArt />
            </div>
          </div>
        </Container>
      </section>

      <Container className="py-14 sm:py-20">
        <div className="grid gap-12 lg:grid-cols-3">
          <div className="space-y-16 lg:col-span-2">
            {/* About */}
            <Reveal>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-500">About this course</h2>
              <div className="mt-3 space-y-4 text-base leading-relaxed text-slate-600">
                <p>{showcase ? firstParagraph : moreParagraphs[0] ?? firstParagraph}</p>
                {(showcase ? moreParagraphs : moreParagraphs.slice(1)).map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
            </Reveal>

            {/* Learning path */}
            <section>
              <Reveal>
                <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-500">Your learning path</h2>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  {lessonCount} steps, one clear journey
                </p>
              </Reveal>
              {course.lessons.length === 0 ? (
                <p className="mt-4 text-sm text-slate-500">Lessons are coming soon.</p>
              ) : (
                <Reveal className="relative mt-8">
                  <span
                    className="path-line absolute bottom-6 left-[23px] top-6 w-0.5 rounded bg-gradient-to-b from-brand-400 via-accent-400 to-brand-400"
                    aria-hidden="true"
                  />
                  <ol className="space-y-4">
                    {course.lessons.map((lesson, index) => {
                      const extra = showcase?.lessons[index]
                      const Icon = extra?.icon ?? GraduationCap
                      return (
                        <li key={lesson.id}>
                          <Reveal delay={index * 90} className="relative flex gap-4">
                            <span className="relative z-10 flex size-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white shadow-[var(--shadow-glow-brand)] ring-4 ring-[var(--color-bg)]">
                              <Icon className="size-5" aria-hidden="true" />
                            </span>
                            <div className="group min-w-0 flex-1 rounded-2xl border border-slate-200 bg-panel p-4 shadow-[var(--shadow-card)] transition-[transform,box-shadow] duration-300 hover:-translate-y-0.5 hover:shadow-[var(--shadow-glow-brand)]">
                              <div className="flex items-start justify-between gap-3">
                                <div className="min-w-0">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-brand-500">
                                    Lesson {index + 1}
                                    {extra && <span className="ml-2 font-medium normal-case text-slate-400">· {extra.minutes} min</span>}
                                  </p>
                                  <p className="mt-1 font-semibold text-slate-900">{lesson.title}</p>
                                  {extra && <p className="mt-1 text-sm text-slate-500">{extra.summary}</p>}
                                </div>
                                <Lock className="mt-1 size-4 shrink-0 text-white/75" aria-label="Enroll to unlock" />
                              </div>
                            </div>
                          </Reveal>
                        </li>
                      )
                    })}
                    <li>
                      <Reveal delay={course.lessons.length * 90} className="relative flex gap-4">
                        <span className="relative z-10 flex size-12 shrink-0 items-center justify-center rounded-2xl bg-amber-400 text-amber-950 shadow-[0_0_24px_-4px_rgb(251_191_36/0.6)] ring-4 ring-[var(--color-bg)]">
                          <Award className="size-5" aria-hidden="true" />
                        </span>
                        <div className="shine relative flex-1 overflow-hidden rounded-2xl border border-amber-400/40 bg-amber-400/10 p-4">
                          <p className="text-xs font-semibold uppercase tracking-wide text-amber-500">Finish line</p>
                          <p className="mt-1 font-semibold text-slate-900">Your WAMUGII certificate</p>
                          <p className="mt-1 text-sm text-slate-600">Complete every lesson and download your certificate of completion.</p>
                        </div>
                      </Reveal>
                    </li>
                  </ol>
                </Reveal>
              )}
            </section>

            {showcase && (
              <section>
                <Reveal>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-500">What you'll be able to do</h2>
                </Reveal>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                  {showcase.outcomes.map(({ icon: Icon, title, text }, i) => (
                    <Reveal key={title} delay={i * 80}>
                      <div className="h-full rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] transition-transform duration-300 hover:-translate-y-1">
                        <span className="flex size-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                          <Icon className="size-5" aria-hidden="true" />
                        </span>
                        <p className="mt-3 font-semibold text-slate-900">{title}</p>
                        <p className="mt-1 text-sm text-slate-500">{text}</p>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </section>
            )}

            {showcase && (
              <section>
                <Reveal>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-500">Who it's for</h2>
                </Reveal>
                <div className="mt-6 grid gap-4 sm:grid-cols-3">
                  {showcase.audience.map(({ icon: Icon, title, text }, i) => (
                    <Reveal key={title} delay={i * 80}>
                      <div className="h-full rounded-2xl border border-slate-200 bg-gradient-to-br from-accent-50/70 to-transparent p-5">
                        <Icon className="size-6 text-accent-600" aria-hidden="true" />
                        <p className="mt-3 font-semibold text-slate-900">{title}</p>
                        <p className="mt-1 text-sm text-slate-500">{text}</p>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </section>
            )}
          </div>

          <aside className="lg:col-span-1">
            <div className="rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm lg:sticky lg:top-24">
              <p className="text-sm font-medium text-slate-500">{course.is_free ? 'This course is' : 'Course price'}</p>
              <p className="mt-1 text-3xl font-bold text-slate-900">{course.is_free ? 'Free' : (price ?? 'Contact us')}</p>
              {!course.is_free && (
                <p className="mt-1 text-xs text-slate-500">
                  We'll generate an invoice; lessons unlock once we've recorded payment.
                </p>
              )}
              <ul className="mt-5 space-y-2.5 text-sm text-slate-600">
                {[
                  `${lessonCount} short lessons with activities`,
                  'Learn at your own pace',
                  showcase ? 'Simple English, no coding needed' : 'Practice in every lesson',
                  'Certificate when you finish',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-500" aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
              <div className="mt-6">{enrollButton(false)}</div>
              {!isAuthenticated && (
                <p className="mt-3 text-center text-xs text-slate-500">You'll be asked to sign in first.</p>
              )}
            </div>
          </aside>
        </div>
      </Container>
    </>
  )
}
