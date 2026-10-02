import { ClipboardList } from 'lucide-react'
import type { QuoteAnswer } from '@/api/quoteRequests'

export interface QuoteAnswersPanelProps {
  answers: QuoteAnswer[]
  /** Addressed to staff by default; the client sees their own words back. */
  audience?: 'staff' | 'client'
}

/**
 * The structured per-service answers on a quote.
 *
 * Renders nothing when there are none, so it can sit unconditionally on both
 * quote-detail pages: a quote for a service with no questions, or one submitted
 * before questions existed, simply shows no extra section.
 *
 * Each label is the question text as stored at submit time, not as the question
 * reads today — that's the point of keeping it on the answer row.
 */
export function QuoteAnswersPanel({ answers, audience = 'staff' }: QuoteAnswersPanelProps) {
  if (answers.length === 0) return null

  return (
    <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
      <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
        <ClipboardList className="size-4" aria-hidden="true" />
        {audience === 'client' ? 'Your answers' : 'Service questionnaire'}
      </h2>
      <p className="mt-1 text-xs text-slate-500">
        {audience === 'client'
          ? 'What you told us when you submitted this request.'
          : 'As asked at submit time — editing a question later never changes this.'}
      </p>

      <dl className="mt-4 divide-y divide-slate-100">
        {answers.map((entry) => (
          <div key={entry.id} className="py-3 first:pt-0 last:pb-0">
            <dt className="text-sm text-slate-500">{entry.question_text}</dt>
            <dd className="mt-1 whitespace-pre-line text-sm font-medium text-slate-900">
              {entry.answer}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
