import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Award,
  BookOpen,
  CheckCircle2,
  Clock,
  Download,
  FileText,
  GraduationCap,
  PlayCircle,
  SearchX,
  Signal,
  SquareTerminal,
  Star,
  Users,
} from 'lucide-react'
import {
  enrollInCourse,
  getPublicCourse,
  listMyEnrollments,
  sampleChapterUrl,
  type ClientEnrollment,
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
import { formatMinutes, getShowcase, groupByModule } from '@/components/courses/courseShowcase'
import { useDocumentTitle } from '@/hooks/useDocumentTitle'
import { CourseReviewsSection, Stars } from '@/components/courses/CourseReviews'
import { CourseFaq } from '@/components/courses/CourseFaq'
import { CODING_COURSES } from '@/lib/python/colab'

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

  // Falls back to "Courses" until the course loads, so the tab never shows a
  // bare site name while the request is in flight.
  useDocumentTitle(course?.title ?? 'Courses', course?.description)

  // A signed-in student who is already enrolled gets "Continue learning" instead of "Enroll".
  const isClient = isAuthenticated && user?.role === 'CLIENT'
  const { data: myEnrollments } = useQuery<ClientEnrollment[], ApiError>({
    queryKey: ['client', 'learning'],
    queryFn: listMyEnrollments,
    enabled: isClient,
  })
  const myEnrollment = myEnrollments?.find((e) => e.course_slug === slug && e.status === 'ACTIVE')

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
  const totalMinutes = course.total_minutes || (showcase ? showcase.hours * 60 : lessonCount * 10)
  const modules = groupByModule(course.lessons)
  const hasWeeks = modules.length > 1 && modules.every((m) => m.title)
  const words = course.title.trim().split(/\s+/)
  const lastWord = words.pop()
  const [firstParagraph, ...moreParagraphs] = course.description.split(/\n\s*\n/)

  const coding = CODING_COURSES.has(course.slug)
  const handbook = course.handbook ?? null
  const rated = course.rating_count > 0 && course.rating_average != null

  const stats = [
    { icon: BookOpen, label: `${lessonCount} lessons` },
    { icon: Clock, label: formatDuration(totalMinutes) },
    { icon: Signal, label: showcase?.level ?? 'Self-paced' },
    { icon: Award, label: 'Certificate' },
    ...(course.student_count > 0
      ? [{ icon: Users, label: `${course.student_count} student${course.student_count === 1 ? '' : 's'} enrolled` }]
      : []),
    ...(handbook ? [{ icon: FileText, label: `${handbook.pages}-page handbook` }] : []),
  ]

  const included = [
    `${lessonCount} lessons with quizzes & activities`,
    ...(handbook ? [`${handbook.pages}-page Student Handbook (PDF) — learn by reading too`] : []),
    ...(coding ? ['Run the Python examples right in your browser'] : []),
    'Learn at your own pace',
    coding ? 'Practice code in every lesson' : 'Simple English, no coding needed',
    'Certificate when you finish',
  ]

  const enrollButton = (dark: boolean) =>
    myEnrollment ? (
      <Link
        to={paths.client.courseDetail(course.slug)}
        className={
          (dark ? 'w-full sm:w-auto shadow-[var(--shadow-glow-brand)] ' : 'w-full ') +
          'inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-base font-semibold text-white transition-opacity hover:opacity-95'
        }
      >
        <PlayCircle className="size-5" aria-hidden="true" />
        {myEnrollment.progress_percent > 0 ? `Continue learning · ${myEnrollment.progress_percent}% done` : 'Start learning'}
        <ArrowRight className="size-4" aria-hidden="true" />
      </Link>
    ) : (
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
      <section className="dark relative overflow-hidden bg-[var(--color-brand-950)]">
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
              {rated && (
                <a
                  href="#reviews"
                  className="hero-in mt-4 inline-flex items-center gap-2 text-sm text-white/85 hover:text-white"
                  style={{ animationDelay: '320ms' }}
                >
                  <span className="text-base font-bold text-amber-300">{course.rating_average!.toFixed(1)}</span>
                  <Stars value={course.rating_average!} size="sm" />
                  <span className="underline-offset-2 hover:underline">
                    ({course.rating_count} rating{course.rating_count === 1 ? '' : 's'})
                  </span>
                </a>
              )}
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
              <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">About this course</h2>
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
                <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Your learning path</h2>
                <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                  {hasWeeks ? `${modules.length} weeks · ${lessonCount} lessons` : `${lessonCount} steps, one clear journey`}
                </p>
              </Reveal>
              {course.lessons.length === 0 ? (
                <p className="mt-4 text-sm text-slate-500">Lessons are coming soon.</p>
              ) : (
                <Reveal className="relative mt-8">
                  <span
                    className="path-line absolute bottom-6 left-[23px] top-6 hidden w-0.5 sm:block rounded bg-gradient-to-b from-brand-400 via-accent-400 to-brand-400"
                    aria-hidden="true"
                  />
                  <ol className="space-y-4">
                    {modules.map((module, mi) => {
                      const week = showcase?.weeks.find((w) => w.title === module.title)
                      const WeekIcon = week?.icon ?? GraduationCap
                      const minutes = module.lessons.reduce((sum, { lesson }) => sum + (lesson.duration_minutes ?? 0), 0)
                      return (
                        <li key={module.title ?? mi}>
                          <Reveal delay={Math.min(mi, 4) * 90} className="relative flex gap-3 sm:gap-4">
                            <span className="relative z-10 hidden size-12 shrink-0 items-center justify-center rounded-2xl sm:flex bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white shadow-[var(--shadow-glow-brand)] ring-4 ring-[var(--color-bg)]">
                              <WeekIcon className="size-5" aria-hidden="true" />
                            </span>
                            <details
                              className="group min-w-0 flex-1 rounded-2xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] transition-shadow duration-300 open:shadow-[var(--shadow-glow-brand)]"
                              open={mi === 0}
                            >
                              <summary className="flex cursor-pointer list-none items-start justify-between gap-3 p-4">
                                <div className="min-w-0">
                                  <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">
                                    {module.title ? module.title.split('·')[0]!.trim() : `Part ${mi + 1}`}
                                    <span className="ml-2 font-medium normal-case text-slate-400">
                                      · {module.lessons.length} lessons{minutes > 0 && ` · ${formatMinutes(minutes)}`}
                                    </span>
                                  </p>
                                  <p className="mt-1 font-semibold text-slate-900">
                                    {module.title?.split('·')[1]?.trim() ?? module.title ?? 'Lessons'}
                                  </p>
                                  {week && <p className="mt-1 text-sm text-slate-500">{week.summary}</p>}
                                </div>
                                <span className="mt-1 text-xs font-semibold text-brand-600 transition-transform duration-300 group-open:rotate-180">▼</span>
                              </summary>
                              <ul className="space-y-1 border-t border-slate-200 px-2 py-3 sm:px-4">
                                {module.lessons.map(({ lesson, index }) => (
                                  <li key={lesson.id}>
                                    <Link
                                      to={`${paths.client.courseDetail(course.slug)}?lesson=${lesson.id}`}
                                      className="group/lesson flex items-center gap-3 rounded-lg px-2 py-2 text-sm transition-colors hover:bg-brand-50"
                                    >
                                      <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-brand-50 text-[11px] font-bold tone-cyan">
                                        {index + 1}
                                      </span>
                                      <span className="min-w-0 flex-1">
                                        <span className="block text-slate-700 group-hover/lesson:text-brand-700">{lesson.title}</span>
                                        {lesson.duration_minutes && (
                                          <span className="mt-0.5 block text-[11px] text-slate-400 sm:hidden">
                                            {lesson.duration_minutes} min{lesson.has_video ? ' · video' : ''}
                                          </span>
                                        )}
                                      </span>
                                      {lesson.duration_minutes && (
                                        <span className="hidden shrink-0 text-xs text-slate-400 sm:inline">{lesson.duration_minutes} min</span>
                                      )}
                                      {lesson.has_video ? (
                                        <PlayCircle className="size-4 shrink-0 text-brand-600 transition-transform group-hover/lesson:scale-125" aria-label="Has video" />
                                      ) : (
                                        <BookOpen className="size-3.5 shrink-0 text-slate-400" aria-label="Reading lesson" />
                                      )}
                                    </Link>
                                  </li>
                                ))}
                              </ul>
                            </details>
                          </Reveal>
                        </li>
                      )
                    })}
                    <li>
                      <Reveal delay={Math.min(modules.length, 5) * 90} className="relative flex gap-4">
                        <span className="relative z-10 hidden size-12 shrink-0 items-center justify-center rounded-2xl sm:flex bg-amber-400 text-amber-950 shadow-[0_0_24px_-4px_rgb(251_191_36/0.6)] ring-4 ring-[var(--color-bg)]">
                          <Award className="size-5" aria-hidden="true" />
                        </span>
                        <div className="shine relative flex-1 overflow-hidden rounded-2xl border border-amber-400/40 bg-amber-400/10 p-4">
                          <p className="text-xs font-semibold uppercase tracking-wide tone-amber">Finish line</p>
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
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">What you'll be able to do</h2>
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
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Who it's for</h2>
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

            {handbook && (
              <section>
                <Reveal>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Learn by reading, too</h2>
                </Reveal>
                <Reveal className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-panel shadow-[var(--shadow-card)]">
                  <div className="grid gap-6 p-5 sm:grid-cols-[auto_1fr] sm:p-6">
                    <div
                      className="dark relative mx-auto flex h-40 w-28 shrink-0 flex-col justify-between overflow-hidden rounded-lg bg-gradient-to-br from-[#0b1120] via-[#0c2a36] to-[#2a1660] p-3 text-white shadow-[var(--shadow-glow-brand)]"
                      aria-hidden="true"
                    >
                      <span className="text-[7px] font-bold uppercase tracking-[0.2em] text-cyan-300">Student Handbook</span>
                      <span className="text-sm font-extrabold leading-tight">{course.title}</span>
                      <span className="h-1 w-8 rounded bg-gradient-to-r from-cyan-400 to-violet-500" />
                    </div>
                    <div>
                      <p className="text-xl font-bold tracking-tight text-slate-900">
                        The complete course in one {handbook.pages}-page book
                      </p>
                      <p className="mt-2 text-sm leading-relaxed text-slate-600">
                        Every lesson becomes a full chapter, written in simple English so you can understand it by reading
                        alone: step-by-step explanations, worked examples, diagrams, common mistakes, examples from Rwanda,
                        self-checks with answers, and a glossary.
                      </p>
                      <ul className="mt-3 flex flex-wrap gap-2 text-xs font-medium text-slate-600">
                        <li className="rounded-full bg-slate-100 px-2.5 py-1">{handbook.chapters} chapters</li>
                        <li className="rounded-full bg-slate-100 px-2.5 py-1">about {Math.round(handbook.words / 1000)},000 words</li>
                        <li className="rounded-full bg-slate-100 px-2.5 py-1">answer key</li>
                        <li className="rounded-full bg-slate-100 px-2.5 py-1">prints well</li>
                      </ul>
                      {handbook.sample_available && (
                        <a
                          href={sampleChapterUrl(course.slug)}
                          className="mt-4 inline-flex items-center gap-2 rounded-lg border border-brand-300 px-3.5 py-2 text-sm font-semibold text-brand-700 transition-colors hover:bg-brand-50"
                        >
                          <Download className="size-4" aria-hidden="true" />
                          Download a free sample chapter (PDF)
                        </a>
                      )}
                    </div>
                  </div>
                </Reveal>
              </section>
            )}

            {coding && (
              <section>
                <Reveal>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Practise as you read</h2>
                </Reveal>
                <Reveal className="mt-6 flex gap-4 rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] sm:p-6">
                  <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-[#0b1220] text-[#67e8f9]">
                    <SquareTerminal className="size-5" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="font-semibold text-slate-900">Run the Python examples right in the lesson</p>
                    <p className="mt-1 text-sm leading-relaxed text-slate-600">
                      Press <b>Run</b> on any code example to run it in your browser, change it, and run it again. No
                      installation and nothing to set up: numpy, pandas, scikit-learn and charts all work on a normal
                      laptop. Every lesson also opens in Google Colab with one click, with a free GPU for the deep-learning examples.
                    </p>
                  </div>
                </Reveal>
              </section>
            )}

            {course.instructors.length > 0 && (
              <section>
                <Reveal>
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">Your instructors</h2>
                </Reveal>
                <div className="mt-6 flex flex-wrap gap-3">
                  {course.instructors.map((name) => (
                    <Reveal key={name}>
                      <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-panel py-2.5 pl-2.5 pr-5">
                        <span className="flex size-10 items-center justify-center rounded-full bg-gradient-to-br from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-sm font-bold text-white">
                          {name
                            .split(/\s+/)
                            .map((w) => w.charAt(0))
                            .slice(0, 2)
                            .join('')}
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-slate-900">{name}</p>
                          <p className="text-xs text-slate-500">Instructor · answers your lesson questions</p>
                        </div>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </section>
            )}

            <CourseReviewsSection slug={course.slug} />

            <CourseFaq isFree={course.is_free} coding={coding} hasHandbook={Boolean(handbook)} />
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
              {rated && (
                <a href="#reviews" className="mt-2 flex items-center gap-1.5 text-sm text-slate-600 hover:text-brand-700">
                  <Star className="size-4 fill-amber-400 text-amber-400" aria-hidden="true" />
                  <span className="font-semibold text-slate-900">{course.rating_average!.toFixed(1)}</span>
                  <span>· {course.rating_count} rating{course.rating_count === 1 ? '' : 's'}</span>
                </a>
              )}
              <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-500">What's included</p>
              <ul className="mt-2.5 space-y-2.5 text-sm text-slate-600">
                {included.map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-600" aria-hidden="true" />
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
