import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, GraduationCap, Lock } from 'lucide-react'
import { listMyEnrollments, type ClientEnrollment } from '@/api/courses'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  ProgressBar,
  Skeleton,
} from '@/components/ui'
import { enrollmentStatusVariant } from '@/utils/statusBadge'

/** The client's My Learning hub — every enrollment with progress. */
export function ClientLearning() {
  const {
    data: enrollments,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['client', 'learning'],
    queryFn: listMyEnrollments,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Learning</h1>
        <p className="mt-1 text-sm text-slate-500">
          Pick up where you left off, or finish a course you've started.
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load your learning"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !enrollments || enrollments.length === 0 ? (
        <EmptyState
          icon={GraduationCap}
          title="No courses yet"
          description="Browse the catalogue and enroll in one that interests you."
          action={
            <Link
              to={paths.courses}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              Explore courses
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {enrollments.map((enrollment) => (
            <EnrollmentCard key={enrollment.id} enrollment={enrollment} />
          ))}
        </div>
      )}
    </div>
  )
}

function EnrollmentCard({ enrollment }: { enrollment: ClientEnrollment }) {
  const isPending = enrollment.status === 'PENDING_PAYMENT'

  return (
    <Link
      to={
        isPending && enrollment.invoice_id
          ? paths.client.invoiceDetail(enrollment.invoice_id)
          : paths.client.courseDetail(enrollment.course_slug)
      }
      className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-panel p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-base font-semibold text-slate-900">{enrollment.course_title}</h2>
        <Badge variant={enrollmentStatusVariant[enrollment.status]}>
          {enrollment.status === 'PENDING_PAYMENT' ? 'Pending payment' : enrollment.status.toLowerCase()}
        </Badge>
      </div>

      {isPending ? (
        <div className="flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
          <Lock className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          <span>
            Complete the invoice to unlock the lessons. We'll email you as soon as payment is
            recorded.
          </span>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              {enrollment.completed_lessons}/{enrollment.total_lessons} lessons complete
            </span>
            <span className="font-medium text-slate-700">{enrollment.progress_percent}%</span>
          </div>
          <ProgressBar value={enrollment.progress_percent} />
        </div>
      )}

      <div className="mt-auto flex items-center justify-end text-sm font-medium text-brand-600">
        {isPending ? 'View invoice' : 'Continue learning'}
        <ArrowRight className="ml-1 size-4" aria-hidden="true" />
      </div>
    </Link>
  )
}
