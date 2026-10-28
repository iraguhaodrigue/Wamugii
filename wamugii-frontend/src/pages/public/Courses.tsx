import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, GraduationCap, Search } from 'lucide-react'
import { listPublicCourses, type Course } from '@/api/courses'
import { paths } from '@/routes/paths'
import { Badge, Container, EmptyState, ErrorState, Input, Skeleton } from '@/components/ui'
import { formatMoney } from '@/utils/format'
import { LottieOnView } from '@/components/common/LottieOnView'

/** Public catalogue: every PUBLISHED, active course. */
export function Courses() {
  const [search, setSearch] = useState('')

  const {
    data: courses,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['courses', 'public'], queryFn: () => listPublicCourses() })

  const filtered = useMemo(() => {
    if (!courses) return []
    const term = search.trim().toLowerCase()
    if (!term) return courses
    return courses.filter(
      (course) =>
        course.title.toLowerCase().includes(term) ||
        course.category?.toLowerCase().includes(term) ||
        course.description.toLowerCase().includes(term),
    )
  }, [courses, search])

  return (
    <Container className="py-16 sm:py-20">
      <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <div className="text-center lg:text-left">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Courses</h1>
          <p className="mt-4 text-base text-slate-500">
            Learn with us. Free courses give instant access; paid courses unlock once we've recorded
            the payment.
          </p>
        </div>

        <LottieOnView
          src="/graphics/lottie/man-robot.json"
          ariaLabel="A person and a robot working side by side at their computers"
          className="mx-auto w-full max-w-[480px]"
          style={{ aspectRatio: '1072 / 574' }}
        />
      </div>

      <div className="relative mx-auto mt-10 max-w-md">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
          aria-hidden="true"
        />
        <Input
          type="search"
          placeholder="Search courses…"
          aria-label="Search courses"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="mt-10">
        {isLoading && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-64 rounded-xl" />
            ))}
          </div>
        )}

        {isError && !isLoading && (
          <ErrorState
            title="Couldn't load courses"
            message="We had trouble reaching the server. Please try again."
            onRetry={() => refetch()}
          />
        )}

        {!isLoading && !isError && courses && courses.length === 0 && (
          <EmptyState
            icon={GraduationCap}
            title="No courses published yet"
            description="Check back soon — we're putting the first courses together."
          />
        )}

        {!isLoading && !isError && courses && courses.length > 0 && filtered.length === 0 && (
          <EmptyState title="No courses match your search" description="Try a different keyword." />
        )}

        {!isLoading && !isError && filtered.length > 0 && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </div>
    </Container>
  )
}

function CourseCard({ course }: { course: Course }) {
  const price = course.is_free ? null : formatMoney(course.price)

  return (
    <Link
      to={paths.courseDetail(course.slug)}
      className="group relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/40 hover:shadow-[var(--shadow-glow-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      <div className="aspect-video w-full overflow-hidden bg-brand-50">
        {course.cover_image_url ? (
          <img
            src={course.cover_image_url}
            alt=""
            className="size-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex size-full items-center justify-center text-brand-500">
            <GraduationCap className="size-10" aria-hidden="true" />
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col p-6">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold text-slate-900">{course.title}</h3>
          {course.is_free ? (
            <Badge variant="success">Free</Badge>
          ) : (
            <Badge variant="brand">{price ?? 'Paid'}</Badge>
          )}
        </div>
        {course.category && (
          <div className="mt-2">
            <Badge variant="neutral">{course.category}</Badge>
          </div>
        )}
        <p className="mt-3 line-clamp-3 text-sm text-slate-500">{course.description}</p>
        <div className="mt-auto flex items-center justify-between pt-5">
          <span className="text-xs text-slate-500">
            {course.lesson_count} lesson{course.lesson_count === 1 ? '' : 's'}
          </span>
          <span className="inline-flex items-center gap-1 text-sm font-medium text-brand-600">
            Learn more
            <ArrowRight
              className="size-4 transition-transform group-hover:translate-x-0.5"
              aria-hidden="true"
            />
          </span>
        </div>
      </div>
    </Link>
  )
}
