import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, GraduationCap, Lock, PlayCircle, SearchX } from 'lucide-react'
import {
  enrollInCourse,
  getPublicCourse,
  type CoursePublicDetail,
  type EnrollResponse,
} from '@/api/courses'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, Container, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatMoney } from '@/utils/format'

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

  return (
    <Container className="py-16 sm:py-20">
      <Link
        to={paths.courses}
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to Courses
      </Link>

      <div className="mt-6 grid gap-10 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="flex size-14 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
            <GraduationCap className="size-7" aria-hidden="true" />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              {course.title}
            </h1>
            {course.category && <Badge variant="brand">{course.category}</Badge>}
            {course.is_free ? (
              <Badge variant="success">Free</Badge>
            ) : (
              <Badge variant="info">{price ?? 'Paid'}</Badge>
            )}
          </div>
          <div className="mt-6 whitespace-pre-line text-base leading-relaxed text-slate-600">
            {course.description}
          </div>

          <section className="mt-10">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              What you'll learn
            </h2>
            {course.lessons.length === 0 ? (
              <p className="mt-4 text-sm text-slate-500">
                Lessons are coming soon.
              </p>
            ) : (
              <ol className="mt-4 space-y-2">
                {course.lessons.map((lesson, index) => (
                  <li
                    key={lesson.id}
                    className="flex items-start gap-3 rounded-lg border border-slate-200 bg-panel p-4"
                  >
                    <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand-700">
                      {index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-900">{lesson.title}</p>
                    </div>
                    <Lock
                      className="size-4 shrink-0 text-slate-300"
                      aria-label="Enroll to unlock"
                    />
                  </li>
                ))}
              </ol>
            )}
          </section>
        </div>

        <aside className="lg:col-span-1">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <p className="text-sm font-medium text-slate-500">
              {course.is_free ? 'This course is' : 'Course price'}
            </p>
            <p className="mt-1 text-2xl font-bold text-slate-900">
              {course.is_free ? 'Free' : (price ?? 'Contact us')}
            </p>
            {!course.is_free && (
              <p className="mt-1 text-xs text-slate-500">
                We'll generate an invoice; lessons unlock once we've recorded payment.
              </p>
            )}

            {enrollError && (
              <p role="alert" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {enrollError}
              </p>
            )}

            <Button
              className="mt-6 w-full"
              size="lg"
              onClick={handleEnroll}
              isLoading={enrollMutation.isPending}
              leftIcon={<PlayCircle className="size-5" />}
            >
              {course.is_free ? 'Enroll — start learning' : 'Enroll and generate invoice'}
            </Button>
            {!isAuthenticated && (
              <p className="mt-3 text-center text-xs text-slate-500">
                You'll be asked to sign in first.
              </p>
            )}
          </div>
        </aside>
      </div>
    </Container>
  )
}
