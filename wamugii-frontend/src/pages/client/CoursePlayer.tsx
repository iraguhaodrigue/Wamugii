import { useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import {
  ArrowLeft,
  Link2,
  ListOrdered,
  PlayCircle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Circle,
  Download,
  FileText,
  Award,
  Lock,
  SearchX,
} from 'lucide-react'
import {
  downloadLessonMaterial,
  enrollInCourse,
  getCertificate,
  getCourseProgress,
  getPublicCourse,
  type CoursePublicDetail,
  listMyEnrollments,
  listMyLessons,
  markLessonComplete,
  type Certificate as CertificateData,
  type ClientEnrollment,
  type Lesson,
} from '@/api/courses'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Button,
  EmptyState,
  ErrorState,
  ProgressBar,
  Skeleton,
} from '@/components/ui'
import { VideoEmbed, VideoPlaceholder } from '@/components/courses/VideoEmbed'
import { Certificate } from '@/components/courses/Certificate'
import { LessonContent, sectionTitles } from '@/components/courses/LessonContent'
import { QuizPanel } from '@/components/courses/QuizPanel'
import { groupByModule } from '@/components/courses/courseShowcase'
import { formatFileSize } from '@/utils/format'
import { cn } from '@/utils/cn'

/** Jump, without animation, so the open lesson's title and video sit just under the sticky top bar. */
function jumpToLesson() {
  const el = document.getElementById('lesson-top')
  if (!el) return
  const stickyHeader = 72
  const top = el.getBoundingClientRect().top + window.scrollY - stickyHeader
  window.scrollTo({ top: Math.max(0, top), left: 0, behavior: 'instant' })
}

/**
 * The course player.
 *
 * Entered by slug (`/client/learning/:slug`) because that's what the public
 * detail page and the My Learning cards link to. Resolves the slug through
 * the public course endpoint, then checks the client's enrollment list for
 * the matching course and decides what to render:
 *
 *  * no enrollment -> 404
 *  * PENDING_PAYMENT -> locked view with a link to the invoice
 *  * ACTIVE -> the real player
 */
export function ClientCoursePlayer() {
  const { slug } = useParams<{ slug: string }>()
  const queryClient = useQueryClient()
  const [activeLessonId, setActiveLessonId] = useState<number | null>(null)
  // `?lesson=<id>` opens that lesson directly (shared links, the course page,
  // emails). The URL is kept in step with the open lesson so every lesson has
  // its own link.
  const [searchParams, setSearchParams] = useSearchParams()
  const requestedLessonId = Number(searchParams.get('lesson')) || null
  const [copied, setCopied] = useState(false)
  // Set when the student picks a lesson; the layout effect below then jumps
  // straight to that lesson's video before the browser paints, so the page
  // never shows a smooth scroll through the top of the page first.
  const pendingScroll = useRef(false)

  // Coming from the course page (or any other page) the window may still be
  // scrolled far down. Start at the top at once: the video sits near the top.
  useLayoutEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [slug])
  const [completeError, setCompleteError] = useState<string | null>(null)
  const [downloadError, setDownloadError] = useState<string | null>(null)
  const [downloadingId, setDownloadingId] = useState<number | null>(null)

  // One public course fetch for the title/lesson count; the catalogue page
  // caches this already so this is usually a no-op.
  const courseQuery = useQuery<CoursePublicDetail | undefined, ApiError>({
    queryKey: ['courses', 'public-detail', slug],
    queryFn: () => getPublicCourse(slug!),
    enabled: Boolean(slug),
  })

  const enrollmentsQuery = useQuery({
    queryKey: ['client', 'learning'],
    queryFn: listMyEnrollments,
  })

  const course = courseQuery.data
  const enrollment: ClientEnrollment | undefined = useMemo(() => {
    if (!course || !enrollmentsQuery.data) return undefined
    return enrollmentsQuery.data.find((e) => e.course_slug === course.slug)
  }, [course, enrollmentsQuery.data])

  const canReadLessons = enrollment?.status === 'ACTIVE'

  const lessonsQuery = useQuery({
    queryKey: ['client', 'learning', course?.id, 'lessons'],
    queryFn: () => listMyLessons(course!.id),
    enabled: Boolean(course && canReadLessons),
  })

  // Exactly which lessons are done -- drives the sidebar ticks.
  const progressQuery = useQuery({
    queryKey: ['client', 'progress', course?.id],
    queryFn: () => getCourseProgress(course!.id),
    enabled: Boolean(course && canReadLessons),
  })
  const completedIds = useMemo(
    () => new Set(progressQuery.data?.completed_lesson_ids ?? []),
    [progressQuery.data],
  )
  const passedQuizIds = useMemo(
    () => new Set(progressQuery.data?.passed_quiz_lesson_ids ?? []),
    [progressQuery.data],
  )

  // Pick the first lesson by default, and keep the choice valid when the list
  // changes under us (soft delete, reorder).
  useEffect(() => {
    const lessons = lessonsQuery.data
    if (!lessons || lessons.length === 0) {
      setActiveLessonId(null)
      return
    }
    if (activeLessonId == null || !lessons.some((l) => l.id === activeLessonId)) {
      // A linked lesson wins; otherwise resume at the first lesson not yet completed.
      const linked = requestedLessonId ? lessons.find((l) => l.id === requestedLessonId) : undefined
      const done = new Set(progressQuery.data?.completed_lesson_ids ?? [])
      const resume = linked ?? lessons.find((l) => !done.has(l.id)) ?? lessons[0]!
      setActiveLessonId(resume.id)
    }
  }, [lessonsQuery.data, activeLessonId, progressQuery.data, requestedLessonId])

  // Keep `?lesson=` in step with the open lesson (replace, so Back still leaves the player).
  useEffect(() => {
    if (activeLessonId == null || requestedLessonId === activeLessonId) return
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev)
        next.set('lesson', String(activeLessonId))
        return next
      },
      { replace: true },
    )
  }, [activeLessonId, requestedLessonId, setSearchParams])

  const enrollMutation = useMutation<unknown, ApiError, number>({
    mutationFn: (courseId) => enrollInCourse(courseId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['client', 'learning'] }),
  })

  const activeLesson: Lesson | undefined = useMemo(
    () => lessonsQuery.data?.find((l) => l.id === activeLessonId),
    [lessonsQuery.data, activeLessonId],
  )

  // Only fetched once the student asks for it: the endpoint 403s until every
  // lesson is complete, so there is nothing to prefetch.
  const [showCertificate, setShowCertificate] = useState(false)
  const certificateQuery = useQuery<CertificateData, ApiError>({
    queryKey: ['client', 'certificate', course?.id],
    queryFn: () => getCertificate(course!.id),
    enabled: showCertificate && Boolean(course),
  })

  const completeMutation = useMutation<unknown, ApiError, number>({
    mutationFn: (lessonId) => markLessonComplete(course!.id, lessonId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client', 'learning'] })
      queryClient.invalidateQueries({ queryKey: ['client', 'progress', course?.id] })
      setCompleteError(null)
    },
    onError: (err) => setCompleteError(err.message),
  })

  // Jump (no animation) to the lesson that was just picked, so its title and
  // video are on screen straight away -- on a phone too, where the lesson list
  // sits below the lesson.
  useLayoutEffect(() => {
    if (!pendingScroll.current || activeLesson == null) return
    pendingScroll.current = false
    jumpToLesson()
  }, [activeLesson])

  const progressText = enrollment
    ? `${enrollment.completed_lessons}/${enrollment.total_lessons} lessons complete`
    : ''

  if (courseQuery.isLoading || enrollmentsQuery.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 rounded-xl" />
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="aspect-video w-full rounded-2xl lg:w-2/3" />
      </div>
    )
  }

  if ((courseQuery.isError && courseQuery.error.status === 404) || !course) {
    return (
      <EmptyState
        icon={SearchX}
        title="Course not found"
        description="This course doesn't exist or isn't published."
        action={
          <Link
            to={paths.client.learning}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to My Learning
          </Link>
        }
      />
    )
  }

  if (enrollmentsQuery.isError) {
    return (
      <ErrorState
        title="Couldn't load your enrollments"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => enrollmentsQuery.refetch()}
      />
    )
  }

  if (!enrollment) {
    return (
      <EmptyState
        icon={Lock}
        title={course.is_free ? `Start ${course.title} — it's free` : "You're not enrolled in this course"}
        description={
          course.is_free
            ? 'Enroll in one click and this lesson opens straight away.'
            : 'Enroll from the course page to unlock the lessons.'
        }
        action={
          course.is_free ? (
            <div className="flex flex-col items-center gap-2">
              <Button
                leftIcon={<PlayCircle className="size-4" />}
                isLoading={enrollMutation.isPending}
                onClick={() => enrollMutation.mutate(course.id)}
              >
                Enroll free & start learning
              </Button>
              {enrollMutation.isError && (
                <p role="alert" className="text-sm text-red-600">
                  {enrollMutation.error.message}
                </p>
              )}
            </div>
          ) : (
            <Link
              to={paths.courseDetail(course.slug)}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              Open the course page
            </Link>
          )
        }
      />
    )
  }

  if (!canReadLessons) {
    return (
      <div className="space-y-6">
        <Link
          to={paths.client.learning}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Learning
        </Link>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">{course.title}</h1>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
          <div className="flex items-start gap-3">
            <Lock className="mt-0.5 size-5 text-amber-700" aria-hidden="true" />
            <div className="space-y-2">
              <h2 className="text-base font-semibold text-amber-900">
                Complete payment to unlock
              </h2>
              <p className="text-sm text-amber-800">
                We've generated an invoice for this course. Your lessons unlock as soon as we've
                recorded the payment -- we'll email you then.
              </p>
              {enrollment.invoice_id && (
                <Link
                  to={paths.client.invoiceDetail(enrollment.invoice_id)}
                  className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-700 hover:text-brand-800"
                >
                  View invoice
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const lessons = lessonsQuery.data ?? []
  const activeIndex = Math.max(0, lessons.findIndex((l) => l.id === activeLessonId))
  const prevLesson = activeIndex > 0 ? lessons[activeIndex - 1] : undefined
  const nextLesson = activeIndex < lessons.length - 1 ? lessons[activeIndex + 1] : undefined
  const lessonText = activeLesson?.content ?? ''
  const sections = sectionTitles(lessonText)
  const readingMinutes = activeLesson?.duration_minutes ?? Math.max(3, Math.round(lessonText.split(/\s+/).length / 180))

  function goTo(lessonId: number) {
    if (lessonId === activeLessonId) {
      // Already open (e.g. tapped again in the list below on a phone): just jump back up to it.
      jumpToLesson()
      return
    }
    pendingScroll.current = true
    setActiveLessonId(lessonId)
  }

  async function copyLessonLink() {
    try {
      await navigator.clipboard.writeText(window.location.href)
      setCopied(true)
      window.setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard blocked (old browser / insecure context): nothing to do.
    }
  }

  if (showCertificate) {
    if (certificateQuery.isLoading) {
      return <Skeleton className="mx-auto aspect-[297/210] w-full max-w-[1000px] rounded-lg" />
    }
    // Never a blank sheet: a failure explains itself and offers a way back.
    if (certificateQuery.isError || !certificateQuery.data) {
      return (
        <ErrorState
          title="Couldn't load your certificate"
          message={
            certificateQuery.error?.status === 403
              ? 'Every lesson needs to be marked complete before the certificate is issued.'
              : "We had trouble reaching the server. Please try again."
          }
          onRetry={() => certificateQuery.refetch()}
        />
      )
    }
    return (
      <Certificate
        certificate={certificateQuery.data}
        onClose={() => setShowCertificate(false)}
      />
    )
  }

  return (
    <div className="space-y-5">
      {/* A slim course bar, so the lesson video is the first big thing on screen. */}
      <div className="rounded-xl border border-slate-200 bg-panel px-3 py-2.5 shadow-[var(--shadow-card)] backdrop-blur-sm sm:px-4">
        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            to={paths.client.learning}
            aria-label="Back to My Learning"
            title="Back to My Learning"
            className="flex size-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-brand-600"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
          </Link>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-slate-900 sm:text-base">{course.title}</p>
            <div className="mt-1 flex items-center gap-2">
              <ProgressBar value={enrollment.progress_percent} className="flex-1" />
              <span className="shrink-0 text-[11px] font-medium text-slate-500" title={progressText}>
                {enrollment.completed_lessons}/{enrollment.total_lessons} · {enrollment.progress_percent}%
              </span>
            </div>
          </div>
          <a
            href="#lesson-list"
            onClick={(e) => {
              e.preventDefault()
              document.getElementById('lesson-list')?.scrollIntoView({ behavior: 'instant', block: 'start' })
            }}
            className="inline-flex h-8 shrink-0 items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 text-xs font-semibold text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 lg:hidden"
          >
            <ListOrdered className="size-4" aria-hidden="true" />
            Lessons
          </a>
        </div>

        {enrollment.progress_percent === 100 && (
          <div className="mt-2.5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-brand-400/30 bg-brand-50 p-3">
            <div className="flex items-center gap-2.5">
              <Award className="size-5 shrink-0 text-brand-600" aria-hidden="true" />
              <p className="text-sm font-semibold text-slate-900">Course complete — your certificate is ready.</p>
            </div>
            <Button size="sm" onClick={() => setShowCertificate(true)}>
              Get your certificate
            </Button>
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <aside id="lesson-list" className="order-last min-w-0 scroll-mt-20 lg:order-first lg:col-span-1">
          <div className="rounded-xl border border-slate-200 bg-panel p-4 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Lessons
            </h2>
            {lessonsQuery.isLoading ? (
              <div className="mt-3 space-y-2">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 rounded-lg" />
                ))}
              </div>
            ) : lessons.length === 0 ? (
              <p className="mt-3 text-sm text-slate-500">No lessons yet.</p>
            ) : (
              <div className="mt-3 space-y-4">
                {groupByModule(lessons).map((module, mi) => {
                  const doneInModule = module.lessons.filter(({ lesson }) => completedIds.has(lesson.id)).length
                  return (
                    <div key={module.title ?? mi}>
                      {module.title && (
                        <div className="mb-1.5 flex items-center justify-between gap-2 px-1">
                          <p className="text-xs font-bold uppercase tracking-wide text-brand-600">{module.title}</p>
                          <span className="text-[11px] font-medium text-slate-400">
                            {doneInModule}/{module.lessons.length}
                          </span>
                        </div>
                      )}
                      <ol className="space-y-1">
                        {module.lessons.map(({ lesson, index }) => {
                          const isActive = lesson.id === activeLessonId
                          const isDone = completedIds.has(lesson.id)
                          return (
                            <li key={lesson.id}>
                              <button
                                type="button"
                                onClick={() => goTo(lesson.id)}
                                className={cn(
                                  'flex w-full items-start gap-2.5 rounded-lg p-2.5 text-left text-sm transition-colors',
                                  isActive
                                    ? 'bg-brand-50 text-slate-900 ring-1 ring-brand-400/40'
                                    : 'text-slate-700 hover:bg-slate-50',
                                )}
                              >
                                {isDone ? (
                                  <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-emerald-500" aria-label="Completed" />
                                ) : (
                                  <Circle className="mt-0.5 size-4 shrink-0 text-slate-300" aria-hidden="true" />
                                )}
                                <span className="min-w-0 flex-1">
                                  <span className="block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                                    Lesson {index + 1}
                                    {lesson.duration_minutes && ` · ${lesson.duration_minutes} min`}
                                    {passedQuizIds.has(lesson.id) && ' · quiz ✓'}
                                  </span>
                                  <span className="font-medium">{lesson.title}</span>
                                </span>
                              </button>
                            </li>
                          )
                        })}
                      </ol>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </aside>

        <section className="min-w-0 space-y-6 lg:col-span-2">
          {!activeLesson ? (
            <EmptyState title="Nothing to show yet" description="This course has no lessons." />
          ) : (
            <>
              <div id="lesson-top" className="scroll-mt-20 space-y-3" key={`top-${activeLesson.id}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] font-bold uppercase tracking-wider text-brand-600 sm:text-xs">
                      <span>
                        {activeLesson.module_title ? `${activeLesson.module_title.split('·')[0]!.trim()} · ` : ''}
                        Lesson {activeIndex + 1} of {lessons.length}
                      </span>
                      <span className="inline-flex items-center gap-1 font-medium normal-case tracking-normal text-slate-400">
                        <Clock className="size-3.5" aria-hidden="true" />
                        about {readingMinutes} min
                      </span>
                    </p>
                    <h2 className="mt-1 text-xl font-bold leading-snug tracking-tight text-slate-900 sm:text-3xl">{activeLesson.title}</h2>
                  </div>
                  <button
                    type="button"
                    onClick={copyLessonLink}
                    aria-label={copied ? 'Link copied' : 'Copy lesson link'}
                    title="Copy lesson link"
                    className="inline-flex h-9 shrink-0 items-center gap-1.5 rounded-lg border border-slate-200 bg-panel px-2.5 text-xs font-semibold text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600 sm:px-3 sm:text-sm"
                  >
                    {copied ? <CheckCircle2 className="size-4 text-emerald-500" aria-hidden="true" /> : <Link2 className="size-4" aria-hidden="true" />}
                    <span className="hidden sm:inline">{copied ? 'Link copied!' : 'Copy lesson link'}</span>
                  </button>
                </div>

                {/* The video comes first: it is what a student opening a lesson link wants to see. */}
                {activeLesson.video_url ? (
                  <div id="lesson-video" className="overflow-hidden rounded-2xl shadow-[var(--shadow-glow-brand)]">
                    <VideoEmbed url={activeLesson.video_url} title={activeLesson.title} />
                  </div>
                ) : null}

                {sections.length > 1 && (
                  <div className="flex flex-wrap gap-2">
                    <span className="self-center text-xs font-semibold uppercase tracking-wide text-slate-400">In this lesson:</span>
                    {sections.map((title, i) => (
                      <a
                        key={i}
                        href={`#lesson-step-${i}`}
                        onClick={(e) => {
                          e.preventDefault()
                          document.getElementById(`lesson-step-${i}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
                        }}
                        className="rounded-full border border-slate-200 bg-panel px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-400 hover:text-brand-600"
                      >
                        {title}
                      </a>
                    ))}
                  </div>
                )}
              </div>
              {activeLesson.content ? (
                <LessonContent content={activeLesson.content} lessonKey={activeLesson.id} />
              ) : (
                !activeLesson.video_url && <VideoPlaceholder />
              )}
              {activeLesson.materials.length > 0 && (
                <div className="rounded-xl border border-slate-200 bg-panel p-6">
                  <h3 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
                    <FileText className="size-4" aria-hidden="true" />
                    Materials
                  </h3>
                  {downloadError && (
                    <p
                      role="alert"
                      className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
                    >
                      {downloadError}
                    </p>
                  )}
                  <ul className="mt-3 space-y-2">
                    {activeLesson.materials.map((material) => (
                      <li
                        key={material.id}
                        className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 p-3 text-sm"
                      >
                        <span className="min-w-0 truncate text-slate-700">
                          {material.original_filename}{' '}
                          <span className="text-xs text-slate-400">
                            ({formatFileSize(material.file_size)})
                          </span>
                        </span>
                        <Button
                          size="sm"
                          variant="outline"
                          isLoading={downloadingId === material.id}
                          leftIcon={<Download className="size-4" />}
                          onClick={async () => {
                            setDownloadError(null)
                            setDownloadingId(material.id)
                            try {
                              await downloadLessonMaterial(
                                course.id,
                                activeLesson.id,
                                material.id,
                                material.original_filename,
                              )
                            } catch {
                              setDownloadError(
                                `Couldn't download ${material.original_filename}. Please try again.`,
                              )
                            } finally {
                              setDownloadingId(null)
                            }
                          }}
                        >
                          Download
                        </Button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {activeLesson.quiz_question_count > 0 && (
                <QuizPanel key={activeLesson.id} courseId={course.id} lessonId={activeLesson.id} />
              )}

              {completeError && (
                <p
                  role="alert"
                  className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
                >
                  {completeError}
                </p>
              )}

              <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <Button
                  variant="outline"
                  disabled={!prevLesson}
                  leftIcon={<ArrowLeft className="size-4" />}
                  onClick={() => prevLesson && goTo(prevLesson.id)}
                >
                  Previous
                </Button>
                <Button
                  isLoading={completeMutation.isPending}
                  leftIcon={<CheckCircle2 className="size-4" />}
                  onClick={() =>
                    completeMutation.mutate(activeLesson.id, {
                      onSuccess: () => {
                        if (nextLesson) goTo(nextLesson.id)
                      },
                    })
                  }
                >
                  {completedIds.has(activeLesson.id) ? (nextLesson ? 'Next lesson' : 'Completed ✓') : nextLesson ? 'Complete & next lesson' : 'Complete course'}
                  {nextLesson && <ArrowRight className="size-4" aria-hidden="true" />}
                </Button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
