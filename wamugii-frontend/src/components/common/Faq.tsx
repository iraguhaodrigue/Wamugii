import { ChevronDown } from 'lucide-react'

export interface FaqItem {
  question: string
  answer: string
}

export interface FaqProps {
  items: FaqItem[]
}

/**
 * Accordion built on native <details>/<summary> rather than JS-managed open
 * state — free keyboard support, screen-reader semantics, and no state
 * management to write. `group-open:` handles the chevron rotation.
 */
export function Faq({ items }: FaqProps) {
  return (
    <div className="divide-y divide-slate-200 rounded-xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] backdrop-blur-sm">
      {items.map((item) => (
        <details key={item.question} className="group px-5 py-4 first:rounded-t-xl last:rounded-b-xl open:bg-white/[0.02] sm:px-6">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-sm font-semibold text-slate-900 marker:content-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 sm:text-base">
            {item.question}
            <ChevronDown
              className="size-4 shrink-0 text-brand-400 transition-transform duration-200 group-open:rotate-180"
              aria-hidden="true"
            />
          </summary>
          <p className="mt-3 text-sm leading-relaxed text-slate-500">{item.answer}</p>
        </details>
      ))}
    </div>
  )
}
