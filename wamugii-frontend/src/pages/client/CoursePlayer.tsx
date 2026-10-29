import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  Download,
  FileText,
  Award,
  Lock,
  SearchX,
} from 'lucide-react'
import {
  downloadLessonMaterial,
  getCertificate,
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
  Badge,
  Button,
  EmptyState,
  ErrorState,
  ProgressBar,
  Skeleton,
} from '@/components/ui'
import { VideoEmbed, VideoPlaceholder } from '@/components/courses/VideoEmbed'
import { Certificate } from '@/components/courses/Certificate'
import { formatFileSize } from '@/utils/format'
import { cn } from '@/utils/cn'

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

  // Pick the first lesson by default, and keep the choice valid when the list
  // changes under us (soft delete, reorder).
  useEffect(() => {
    const lessons = lessonsQuery.data
    if (!lessons || lessons.length === 0) {
      setActiveLessonId(null)
      return
    }
    if (activeLessonId == null || !lessons.some((l) => l.id === activeLessonId)) {
      setActiveLessonId(lessons[0]!.id)
    }
  }, [lessonsQuery.data, activeLessonId])

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
      setCompleteError(null)
    },
    onError: (err) => setCompleteError(err.message),
  })

  // We don't have per-lesson completion detail on the client. Derive which
  // lessons are completed from the enrollment counts across sequential marks
  // -- "complete" buttons stay enabled; the progress bar is the source of
  // truth for the overall picture.
  const progressText = enrollment
    ? `${enrollment.completed_lessons}/${enrollment.total_lessons} lessons complete`
    : ''

  if (courseQuery.isLoading || enrollmentsQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
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
        title="You're not enrolled in this course"
        description="Enroll from the catalogue to unlock the lessons."
        action={
          <Link
            to={paths.courseDetail(course.slug)}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            Open the course page
          </Link>
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
    <div className="space-y-6">
      <div>
        <Link
          to={paths.client.learning}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to My Learning
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{course.title}</h1>
          <Badge variant="success">Active</Badge>
        </div>
        <div className="mt-3 space-y-1.5">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>{progressText}</span>
            <span className="font-medium text-slate-700">{enrollment.progress_percent}%</span>
          </div>
          <ProgressBar value={enrollment.progress_percent} />
        </div>

        {enrollment.progress_percent === 100 && (
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-brand-400/30 bg-brand-50 p-4">
            <div className="flex items-start gap-3">
              <Award className="mt-0.5 size-5 shrink-0 text-brand-600" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-slate-900">Course complete</p>
                <p className="mt-0.5 text-sm text-slate-500">
                  You've finished every lesson — your certificate is ready.
                </p>
              </div>
            </div>
            <Button size="sm" onClick={() => setShowCertificate(true)}>
              Get your certificate
            </Button>
          </div>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <aside className="order-last lg:order-first lg:col-span-1">
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
              <ol className="mt-3 space-y-1">
                {lessons.map((lesson, index) => {
                  const isActive = lesson.id === activeLessonId
                  // Simple heuristic: the first N by order are "done" when N
                  // matches completed_lessons. Not authoritative, but close
                  // enough to tick off a sidebar; the server has the truth.
                  const isLikelyComplete = index < enrollment.completed_lessons
                  return (
                    <li key={lesson.id}>
                      <button
                        type="button"
                        onClick={() => setActiveLessonId(lesson.id)}
                        className={cn(
                          'flex w-full items-start gap-2.5 rounded-lg p-2.5 text-left text-sm transition-colors',
                          isActive
                            ? 'bg-brand-50 text-brand-900'
                            : 'text-slate-700 hover:bg-slate-50',
                        )}
                      >
                        {isLikelyComplete ? (
                          <CheckCircle2
                            className="mt-0.5 size-4 shrink-0 text-brand-500"
                            aria-hidden="true"
                          />
                        ) : (
                          <Circle
                            className="mt-0.5 size-4 shrink-0 text-slate-300"
                            aria-hidden="true"
                          />
                        )}
                        <span className="min-w-0 flex-1">
                          <span className="font-medium">{lesson.title}</span>
                        </span>
                      </button>
                    </li>
                  )
                })}
              </ol>
            )}
          </div>
        </aside>

        <section className="space-y-6 lg:col-span-2">
          {!activeLesson ? (
            <EmptyState title="Nothing to show yet" description="This course has no lessons." />
          ) : (
            <>
              <h2 className="text-xl font-semibold text-slate-900">{activeLesson.title}</h2>
              {activeLesson.video_url ? (
                <VideoEmbed url={activeLesson.video_url} title={activeLesson.title} />
              ) : (
                <VideoPlaceholder />
              )}
              {activeLesson.content && (
                <div className="whitespace-pre-line rounded-xl border border-slate-200 bg-panel p-6 text-sm leading-relaxed text-slate-700">
                  {activeLesson.content}
                </div>
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

              {completeError && (
                <p
                  role="alert"
                  className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700"
                >
                  {completeError}
                </p>
              )}

              <div className="flex justify-end">
                <Button
                  isLoading={completeMutation.isPending}
                  leftIcon={<CheckCircle2 className="size-4" />}
                  onClick={() => completeMutation.mutate(activeLesson.id)}
                >
                  Mark lesson complete
                </Button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
