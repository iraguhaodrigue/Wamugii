import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Search, Sparkles } from 'lucide-react'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { cn } from '@/utils/cn'

/**
 * Each prompt is a plain-language way a business owner might describe their
 * need, mapped to terms we match against the *real* service catalogue. No
 * results are invented — if nothing matches, the panel routes to the quote
 * form instead of pretending to have an answer.
 */
const prompts = [
  { label: 'Build my business website', terms: ['web', 'design', 'development'] },
  { label: 'Create custom software', terms: ['software', 'development'] },
  { label: 'Run my project end to end', terms: ['project'] },
  { label: 'Set up hosting & domains', terms: ['hosting', 'domain'] },
  { label: 'Improve my IT setup', terms: ['it', 'installation', 'consultancy'] },
  { label: 'Get technical support', terms: ['support', 'research', 'technical'] },
]

export interface ServiceExplorerProps {
  services: Service[]
  isLoading?: boolean
}

function matches(service: Service, terms: string[]): boolean {
  const haystack = [service.name, service.short_description, service.category]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
  return terms.some((term) => haystack.includes(term))
}

export function ServiceExplorer({ services, isLoading = false }: ServiceExplorerProps) {
  const [query, setQuery] = useState('')
  const [activePrompt, setActivePrompt] = useState<string | null>(null)

  const results = useMemo(() => {
    const typed = query.trim().toLowerCase()
    const terms = typed
      ? typed.split(/\s+/)
      : (prompts.find((p) => p.label === activePrompt)?.terms ?? [])
    if (terms.length === 0) return []
    return services.filter((service) => matches(service, terms)).slice(0, 4)
  }, [query, activePrompt, services])

  const hasSearched = query.trim().length > 0 || activePrompt !== null

  return (
    <div className="mx-auto mt-12 max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-md sm:p-5">
      <label htmlFor="service-explorer" className="flex items-center gap-2 text-xs font-medium text-brand-300">
        <Sparkles className="size-3.5" aria-hidden="true" />
        What does your business need?
      </label>

      <div className="relative mt-3">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
          aria-hidden="true"
        />
        <input
          id="service-explorer"
          type="search"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setActivePrompt(null)
          }}
          placeholder="Describe it in your own words…"
          className="h-12 w-full rounded-xl border border-white/10 bg-black/30 pl-10 pr-3 text-sm text-slate-900 placeholder:text-slate-400 focus-visible:border-brand-400/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
        />
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {prompts.map((prompt) => (
          <button
            key={prompt.label}
            type="button"
            onClick={() => {
              setActivePrompt((current) => (current === prompt.label ? null : prompt.label))
              setQuery('')
            }}
            className={cn(
              'rounded-full border px-3 py-1.5 text-xs font-medium transition-colors',
              activePrompt === prompt.label
                ? 'border-brand-400/50 bg-brand-500/15 text-brand-300'
                : 'border-white/10 bg-white/5 text-slate-400 hover:border-brand-400/30 hover:text-slate-900',
            )}
          >
            {prompt.label}
          </button>
        ))}
      </div>

      {hasSearched && (
        <div className="mt-4 border-t border-white/10 pt-4 text-left">
          {isLoading ? (
            <p className="text-sm text-slate-400">Loading services…</p>
          ) : results.length > 0 ? (
            <ul className="space-y-1.5">
              {results.map((service) => (
                <li key={service.id}>
                  <Link
                    to={paths.serviceDetail(service.id)}
                    className="group flex items-center justify-between gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors hover:bg-white/5"
                  >
                    <span className="font-medium text-slate-900">{service.name}</span>
                    <ArrowRight
                      className="size-4 shrink-0 text-brand-400 transition-transform group-hover:translate-x-0.5"
                      aria-hidden="true"
                    />
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex flex-wrap items-center justify-between gap-3 px-3 py-1">
              <p className="text-sm text-slate-400">No direct match — tell us about it and we'll advise.</p>
              <Link
                to={paths.requestQuote}
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-400 hover:text-brand-300"
              >
                Request a quote
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
