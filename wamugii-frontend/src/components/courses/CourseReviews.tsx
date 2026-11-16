import { useState } from 'react'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { MessageSquareQuote, Star, Trash2 } from 'lucide-react'
import {
  deleteMyReview,
  getCourseReviews,
  getMyReview,
  saveMyReview,
  type CourseReviewsPage,
  type MyReviewStatus,
} from '@/api/courses'
import type { ApiError } from '@/lib/apiClient'
import { Button } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'

/** Read-only stars. Supports halves, e.g. 4.5. */
export function Stars({ value, size = 'md', className }: { value: number; size?: 'sm' | 'md' | 'lg'; className?: string }) {
  const px = size === 'sm' ? 'size-3.5' : size === 'lg' ? 'size-6' : 'size-4'
  return (
    <span className={cn('inline-flex items-center gap-0.5', className)} role="img" aria-label={`${value.toFixed(1)} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map((i) => {
        const fill = Math.max(0, Math.min(1, value - (i - 1)))
        return (
          <span key={i} className={cn('relative inline-block', px)}>
            <Star className={cn('absolute inset-0 text-slate-300', px)} aria-hidden="true" />
            <span className="absolute inset-0 overflow-hidden" style={{ width: `${fill * 100}%` }}>
              <Star className={cn('fill-amber-400 text-amber-400', px)} aria-hidden="true" />
            </span>
          </span>
        )
      })}
    </span>
  )
}

const LABELS = ['', 'Poor', 'Fair', 'Good', 'Very good', 'Excellent']

function StarInput({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  const [hover, setHover] = useState(0)
  const shown = hover || value
  return (
    <div className="flex items-center gap-3">
      <div className="flex gap-1" role="radiogroup" aria-label="Your rating" onMouseLeave={() => setHover(0)}>
        {[1, 2, 3, 4, 5].map((i) => (
          <button
            key={i}
            type="button"
            role="radio"
            aria-checked={value === i}
            aria-label={`${i} star${i === 1 ? '' : 's'}: ${LABELS[i]}`}
            onMouseEnter={() => setHover(i)}
            onFocus={() => setHover(i)}
            onBlur={() => setHover(0)}
            onClick={() => onChange(i)}
            className="rounded-md p-0.5 transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
          >
            <Star className={cn('size-7', i <= shown ? 'fill-amber-400 text-amber-400' : 'text-slate-300')} aria-hidden="true" />
          </button>
        ))}
      </div>
      {shown > 0 && <span className="text-sm font-medium text-slate-600">{LABELS[shown]}</span>}
    </div>
  )
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' })
}

/** The public "What students say" section on a course page. */
export function CourseReviewsSection({ slug }: { slug: string }) {
  const pageSize = 6
  const query = useInfiniteQuery<CourseReviewsPage, ApiError>({
    queryKey: ['courses', 'reviews', slug],
    queryFn: ({ pageParam }) => getCourseReviews(slug, pageSize, pageParam as number),
    initialPageParam: 0,
    getNextPageParam: (last, pages) => {
      const loaded = pages.reduce((n, p) => n + p.reviews.length, 0)
      return loaded < last.total_with_comments ? loaded : undefined
    },
  })
  const first = query.data?.pages[0]
  if (!first || first.summary.count === 0) return null
  const { summary } = first
  const reviews = query.data!.pages.flatMap((p) => p.reviews)

  return (
    <section id="reviews" className="scroll-mt-24">
      <Reveal>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-brand-600">What students say</h2>
      </Reveal>
      <Reveal className="mt-6 grid gap-6 rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] sm:grid-cols-[auto_1fr] sm:p-6">
        <div className="text-center sm:pr-6 sm:text-left">
          <p className="text-5xl font-extrabold tracking-tight text-slate-900">{summary.average?.toFixed(1)}</p>
          <Stars value={summary.average ?? 0} size="md" className="mt-2" />
          <p className="mt-1.5 text-sm text-slate-500">
            {summary.count} rating{summary.count === 1 ? '' : 's'}
          </p>
        </div>
        <ul className="space-y-1.5 self-center">
          {['5', '4', '3', '2', '1'].map((star) => {
            const n = summary.distribution?.[star] ?? 0
            const pct = summary.count ? Math.round((n / summary.count) * 100) : 0
            return (
              <li key={star} className="flex items-center gap-2.5 text-xs text-slate-500">
                <span className="w-10 shrink-0">{star} star{star === '1' ? '' : 's'}</span>
                <span className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                  <span className="block h-full rounded-full bg-amber-400" style={{ width: `${pct}%` }} />
                </span>
                <span className="w-9 shrink-0 text-right tabular-nums">{pct}%</span>
              </li>
            )
          })}
        </ul>
      </Reveal>
      {reviews.length > 0 && (
        <div className="mt-5 grid gap-4 sm:grid-cols-2">
          {reviews.map((r, i) => (
            <Reveal key={r.id} delay={Math.min(i, 5) * 60}>
              <figure className="h-full rounded-2xl border border-slate-200 bg-panel p-5">
                <div className="flex items-center justify-between gap-3">
                  <Stars value={r.rating} size="sm" />
                  <span className="text-xs text-slate-400">{formatDate(r.updated_at)}</span>
                </div>
                <blockquote className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-600">{r.comment}</blockquote>
                <figcaption className="mt-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
                  <span className="flex size-7 items-center justify-center rounded-full bg-brand-50 text-xs font-bold text-brand-700">
                    {r.reviewer_name.charAt(0)}
                  </span>
                  {r.reviewer_name}
                  <span className="text-xs font-normal text-slate-400">· verified student</span>
                </figcaption>
              </figure>
            </Reveal>
          ))}
        </div>
      )}
      {query.hasNextPage && (
        <div className="mt-5 text-center">
          <Button variant="outline" size="sm" onClick={() => query.fetchNextPage()} isLoading={query.isFetchingNextPage}>
            Show more reviews
          </Button>
        </div>
      )}
    </section>
  )
}

/**
 * The student's own rating card in the course player. Hidden until they have
 * done enough of the course to rate it (the server decides), unless they
 * already left a review.
 */
export function RateCourseCard({ courseId, completedLessons }: { courseId: number; completedLessons: number }) {
  const queryClient = useQueryClient()
  const key = ['client', 'review', courseId, completedLessons]
  const { data } = useQuery<MyReviewStatus, ApiError>({ queryKey: key, queryFn: () => getMyReview(courseId) })
  const [editing, setEditing] = useState(false)
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')
  const [error, setError] = useState<string | null>(null)

  const save = useMutation<MyReviewStatus, ApiError>({
    mutationFn: () => saveMyReview(courseId, { rating, comment: comment.trim() || null }),
    onSuccess: (status) => {
      queryClient.setQueryData(key, status)
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setEditing(false)
      setError(null)
    },
    onError: (e) => setError(e.message),
  })
  const remove = useMutation<void, ApiError>({
    mutationFn: () => deleteMyReview(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client', 'review', courseId] })
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setEditing(false)
    },
    onError: (e) => setError(e.message),
  })

  if (!data || (!data.can_review && !data.review)) return null
  const mine = data.review

  function startEditing() {
    setRating(mine?.rating ?? 0)
    setComment(mine?.comment ?? '')
    setError(null)
    setEditing(true)
  }

  return (
    <div className="rounded-2xl border border-amber-300/50 bg-gradient-to-br from-amber-50/80 to-transparent p-4 sm:p-5">
      <div className="flex items-start gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-amber-400/20 text-amber-600">
          <MessageSquareQuote className="size-5" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          {mine && !editing ? (
            <>
              <p className="text-sm font-semibold text-slate-900">Thank you for rating this course</p>
              <Stars value={mine.rating} size="sm" className="mt-1.5" />
              {mine.comment && <p className="mt-2 whitespace-pre-line text-sm text-slate-600">{mine.comment}</p>}
              <div className="mt-3 flex flex-wrap gap-2">
                <Button size="sm" variant="outline" onClick={startEditing}>
                  Edit my review
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => remove.mutate()}
                  isLoading={remove.isPending}
                  leftIcon={<Trash2 className="size-4" />}
                >
                  Delete
                </Button>
              </div>
            </>
          ) : !editing ? (
            <>
              <p className="text-sm font-semibold text-slate-900">How is the course so far?</p>
              <p className="mt-0.5 text-sm text-slate-600">Your rating helps other students choose, and helps us improve the lessons.</p>
              <Button size="sm" className="mt-3" onClick={startEditing} leftIcon={<Star className="size-4" />}>
                Rate this course
              </Button>
            </>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (!rating) {
                  setError('Choose from 1 to 5 stars.')
                  return
                }
                save.mutate()
              }}
            >
              <p className="text-sm font-semibold text-slate-900">Your rating</p>
              <div className="mt-2">
                <StarInput value={rating} onChange={setRating} />
              </div>
              <label className="mt-3 block text-sm font-medium text-slate-700" htmlFor={`review-${courseId}`}>
                What did you like, and what could be better? <span className="font-normal text-slate-400">(optional)</span>
              </label>
              <textarea
                id={`review-${courseId}`}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                maxLength={1000}
                rows={3}
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
                placeholder="For example: the examples about mobile money made it easy to understand."
              />
              <p className="mt-1 text-xs text-slate-400">
                Shown on the course page with your first name and initial. {1000 - comment.length} characters left.
              </p>
              {error && (
                <p role="alert" className="mt-2 text-sm text-red-600">
                  {error}
                </p>
              )}
              <div className="mt-3 flex gap-2">
                <Button size="sm" type="submit" isLoading={save.isPending}>
                  Save my review
                </Button>
                <Button size="sm" variant="ghost" type="button" onClick={() => setEditing(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
