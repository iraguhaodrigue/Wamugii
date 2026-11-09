import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, GraduationCap, Search } from 'lucide-react'
import { listPublicCourses, type Course } from '@/api/courses'
import { paths } from '@/routes/paths'
import { Badge, Container, EmptyState, ErrorState, Input, Skeleton } from '@/components/ui'
import { formatMoney } from '@/utils/format'
import { LottieOnView } from '@/components/common/LottieOnView'
import { PageHeader } from '@/components/common/PageHeader'
import { Reveal } from '@/components/common/Reveal'
import { ProgramArt, type ProgramArtKind } from '@/components/home/ProgramArt'

/** Each AI Program course gets its own animated cover (the same art as on the homepage). */
const COURSE_ART: Record<string, { kind: ProgramArtKind; glow: string }> = {
  'ai-career-essentials': { kind: 'career', glow: 'from-cyan-500/30' },
  'ai-foundations': { kind: 'foundations', glow: 'from-violet-500/30' },
  'math-python-for-ai': { kind: 'mathpython', glow: 'from-emerald-500/30' },
  'machine-learning-fundamentals': { kind: 'ml', glow: 'from-fuchsia-500/30' },
  'deep-learning-neural-networks': { kind: 'deep', glow: 'from-pink-500/30' },
  'modern-ai-llms-generative': { kind: 'llm', glow: 'from-amber-500/30' },
  'responsible-ai-deployment': { kind: 'deploy', glow: 'from-green-500/30' },
}

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
    <>
    <PageHeader
      eyebrow="WAMUGII Academy"
      title="Learn with"
      highlight="WAMUGII"
      description="Practical courses in simple English, from your first AI prompt to deploying real AI. Free courses give instant access; paid courses unlock once we've recorded the payment."
      art={
        <LottieOnView
          src="/graphics/lottie/man-robot.json"
          ariaLabel="A person and a robot working side by side at their computers"
          className="mx-auto w-full max-w-[480px]"
          style={{ aspectRatio: '1072 / 574' }}
        />
      }
    >
      <div className="relative max-w-md">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 z-10 size-4 -translate-y-1/2 text-slate-400"
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
    </PageHeader>
    <Container className="py-12 sm:py-16">
      <div>
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
            {filtered.map((course, index) => (
              <Reveal key={course.id} delay={(index % 3) * 80} className="h-full">
                <CourseCard course={course} />
              </Reveal>
            ))}
          </div>
        )}
      </div>
    </Container>
    </>
  )
}

function CourseCard({ course }: { course: Course }) {
  const price = course.is_free ? null : formatMoney(course.price)

  return (
    <Link
      to={paths.courseDetail(course.slug)}
      className="group relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/40 hover:shadow-[var(--shadow-glow-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      <div className="relative aspect-video w-full overflow-hidden bg-brand-50">
        {COURSE_ART[course.slug] && !course.cover_image_url ? (
          <div className="relative size-full bg-[#06131c]">
            <div className={`pointer-events-none absolute inset-0 bg-gradient-to-b to-transparent ${COURSE_ART[course.slug]!.glow}`} aria-hidden="true" />
            <div className="relative size-full p-3 transition-transform duration-500 group-hover:scale-[1.05]">
              <ProgramArt kind={COURSE_ART[course.slug]!.kind} />
            </div>
          </div>
        ) : course.cover_image_url ? (
          <img
            src={course.cover_image_url}
            alt=""
            className="size-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="flex size-full items-center justify-center text-brand-600">
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
