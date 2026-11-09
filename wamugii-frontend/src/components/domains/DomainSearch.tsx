import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { AlertTriangle, ArrowRight, CheckCircle2, Globe, Info, Lightbulb, Search, XCircle } from 'lucide-react'
import {
  listPublicExtensions,
  orderDomain,
  searchDomains,
  type DomainCheckResult,
} from '@/api/domains'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Button, Modal, Skeleton } from '@/components/ui'
import { formatDate, formatMoney } from '@/utils/format'
import { cn } from '@/utils/cn'

interface DomainSearchProps {
  /** "public": the marketing page; "client": inside the client portal. */
  mode: 'public' | 'client'
}

/**
 * Search box + live availability results + "Get it" ordering.
 *
 * The query lives in the URL (?q=…) so results can be shared and survive the
 * sign-in round trip: a visitor who clicks "Get it" is sent to sign in and
 * comes back to /client/domains/find?q=…&order=<domain> with the order form
 * already open.
 */
export function DomainSearch({ mode }: DomainSearchProps) {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const [text, setText] = useState(q)
  const [ordering, setOrdering] = useState<DomainCheckResult | null>(null)
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => setText(q), [q])

  const prices = useQuery({ queryKey: ['domains', 'extensions', 'public'], queryFn: listPublicExtensions })
  const search = useQuery({
    queryKey: ['domains', 'search', q],
    queryFn: () => searchDomains(q),
    enabled: q.trim().length > 0,
    staleTime: 60_000,
    retry: false,
  })

  // Coming back from sign-in with ?order=<domain>: open the order form.
  const orderParam = params.get('order')
  useEffect(() => {
    if (!orderParam || !search.data || mode !== 'client') return
    const all = [...search.data.results, ...search.data.suggestions]
    const hit = all.find((r) => r.domain === orderParam && r.status !== 'taken' && r.price)
    if (hit) setOrdering(hit)
    const next = new URLSearchParams(params)
    next.delete('order')
    setParams(next, { replace: true })
  }, [orderParam, search.data, mode, params, setParams])

  function submit(e: FormEvent) {
    e.preventDefault()
    const value = text.trim()
    if (!value) return
    setParams({ q: value })
  }

  function getIt(result: DomainCheckResult) {
    if (isAuthenticated && user?.role === 'CLIENT') {
      setOrdering(result)
      return
    }
    navigate(paths.login, {
      state: {
        from: {
          pathname: paths.client.findDomain,
          search: `?q=${encodeURIComponent(result.domain)}&order=${encodeURIComponent(result.domain)}`,
        },
      },
    })
  }

  const error = search.error as ApiError | null
  const results = search.data?.results ?? []
  const [primary, ...others] = results

  return (
    <div className="space-y-6">
      <form
        onSubmit={submit}
        role="search"
        className="rounded-2xl border border-slate-200 bg-panel p-3 shadow-[var(--shadow-card)] sm:p-4"
      >
        <label htmlFor="domain-search" className="sr-only">
          Domain name
        </label>
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Globe className="pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              id="domain-search"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type a name, e.g. kigalishop or kigalishop.rw"
              autoComplete="off"
              autoCapitalize="none"
              spellCheck={false}
              maxLength={120}
              className="h-14 w-full rounded-xl border border-slate-200 bg-transparent pl-12 pr-4 text-base text-slate-900 placeholder:text-slate-400 focus-visible:border-brand-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400/30"
            />
          </div>
          <Button type="submit" size="lg" className="h-14 sm:w-40" isLoading={search.isFetching} leftIcon={<Search className="size-5" />}>
            Search
          </Button>
        </div>
        {prices.data && prices.data.length > 0 && (
          <ul className="mt-3 flex flex-wrap gap-2" aria-label="Extensions and yearly prices">
            {prices.data.map((p) => (
              <li key={p.extension} className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600">
                <span className="font-semibold text-slate-900">{p.extension}</span> {formatMoney(p.client_price)}/yr
              </li>
            ))}
          </ul>
        )}
      </form>

      {search.isFetching && !search.data && (
        <div className="space-y-3" aria-busy="true" aria-label="Checking availability">
          <Skeleton className="h-28 rounded-2xl" />
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-xl" />
          ))}
        </div>
      )}

      {error && !search.isFetching && (
        <p role="alert" className="flex items-start gap-2 rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          {error.status === 429 ? 'Too many searches in a short time. Please wait a minute and try again.' : error.message}
        </p>
      )}

      {primary && (
        <div className="space-y-6" aria-live="polite">
          <PrimaryResult result={primary} onGet={getIt} />

          {search.data!.suggestions.length > 0 && (
            <section>
              <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-600">
                <Lightbulb className="size-4 tone-amber" aria-hidden="true" />
                Similar names that are free
              </h2>
              <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                {search.data!.suggestions.map((r) => (
                  <ResultRow key={r.domain} result={r} onGet={getIt} compact />
                ))}
              </ul>
            </section>
          )}

          {others.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-600">Other extensions</h2>
              <ul className="mt-3 space-y-2">
                {others.map((r) => (
                  <ResultRow key={r.domain} result={r} onGet={getIt} />
                ))}
              </ul>
            </section>
          )}

          <p className="flex items-start gap-2 text-xs text-slate-500">
            <Info className="mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            {search.data!.note}
          </p>
        </div>
      )}

      {ordering && <OrderModal result={ordering} onClose={() => setOrdering(null)} />}
    </div>
  )
}

function StatusPill({ result }: { result: DomainCheckResult }) {
  if (result.status === 'available')
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold tone-emerald">
        <CheckCircle2 className="size-3.5" aria-hidden="true" /> Available
      </span>
    )
  if (result.status === 'taken')
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-slate-500/10 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
        <XCircle className="size-3.5" aria-hidden="true" /> Taken
      </span>
    )
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-0.5 text-xs font-semibold tone-amber">
      <AlertTriangle className="size-3.5" aria-hidden="true" /> Not confirmed
    </span>
  )
}

function DomainName({ domain, extension, large }: { domain: string; extension: string; large?: boolean }) {
  const name = domain.slice(0, domain.length - extension.length)
  return (
    <span className={cn('break-all font-semibold text-slate-900', large ? 'text-2xl sm:text-3xl' : 'text-base')}>
      {name}
      <span className="tone-cyan">{extension}</span>
    </span>
  )
}

function Action({ result, onGet }: { result: DomainCheckResult; onGet: (r: DomainCheckResult) => void }) {
  if (result.status === 'taken') return null
  if (!result.price)
    return (
      <Link
        to={`${paths.requestQuote}?service=domain&domain=${encodeURIComponent(result.domain)}`}
        className="inline-flex h-10 items-center gap-1.5 rounded-lg border border-slate-300 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-100"
      >
        Ask us <ArrowRight className="size-4" aria-hidden="true" />
      </Link>
    )
  return (
    <Button onClick={() => onGet(result)} rightIcon={<ArrowRight className="size-4" />}>
      {result.status === 'available' ? 'Get it' : 'Request it'}
    </Button>
  )
}

function Detail({ result }: { result: DomainCheckResult }) {
  if (result.status === 'taken')
    return (
      <span className="text-sm text-slate-500">
        {result.expires_at ? `Registered until ${formatDate(result.expires_at)}` : 'Already registered'}
        {result.registrar ? ` · ${result.registrar}` : ''}
      </span>
    )
  if (result.status === 'unknown')
    return <span className="text-sm text-slate-500">{result.reason ?? "We couldn't check this one right now."}</span>
  return result.price ? (
    <span className="text-sm text-slate-600">
      <span className="font-semibold text-slate-900">{formatMoney(result.price)}</span> per year
    </span>
  ) : (
    <span className="text-sm text-slate-500">Free to register — ask us for the price</span>
  )
}

function PrimaryResult({ result, onGet }: { result: DomainCheckResult; onGet: (r: DomainCheckResult) => void }) {
  const free = result.status === 'available'
  return (
    <div
      className={cn(
        'flex flex-col gap-4 rounded-2xl border p-5 sm:flex-row sm:items-center sm:justify-between sm:p-6',
        free ? 'border-emerald-400/50 bg-emerald-500/5' : 'border-slate-200 bg-panel',
      )}
    >
      <div className="min-w-0 space-y-2">
        <StatusPill result={result} />
        <div>
          <DomainName domain={result.domain} extension={result.extension} large />
        </div>
        <Detail result={result} />
      </div>
      <Action result={result} onGet={onGet} />
    </div>
  )
}

function ResultRow({
  result,
  onGet,
  compact,
}: {
  result: DomainCheckResult
  onGet: (r: DomainCheckResult) => void
  compact?: boolean
}) {
  return (
    <li
      className={cn(
        'flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-panel px-4 py-3',
        result.status === 'taken' && 'bg-transparent',
      )}
    >
      <div className="min-w-0 space-y-1">
        <div className="flex flex-wrap items-center gap-2">
          <DomainName domain={result.domain} extension={result.extension} />
          {!compact && <StatusPill result={result} />}
        </div>
        <Detail result={result} />
      </div>
      <Action result={result} onGet={onGet} />
    </li>
  )
}

function OrderModal({ result, onClose }: { result: DomainCheckResult; onClose: () => void }) {
  const [years, setYears] = useState(1)
  const queryClient = useQueryClient()
  const total = useMemo(() => (result.price ? String(Number(result.price) * years) : null), [result.price, years])
  const order = useMutation({
    mutationFn: () => orderDomain({ domain_name: result.domain, years }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client', 'domains'] })
      queryClient.invalidateQueries({ queryKey: ['domains', 'search'] })
    },
  })
  const error = order.error as ApiError | null

  return (
    <Modal isOpen onClose={onClose} title={order.isSuccess ? 'Request received' : 'Get this domain'}>
      {order.isSuccess ? (
        <div className="space-y-4">
          <p className="flex items-start gap-2 text-sm text-slate-700">
            <CheckCircle2 className="mt-0.5 size-5 shrink-0 tone-emerald" aria-hidden="true" />
            <span>
              We received your request for <strong className="text-slate-900">{result.domain}</strong>. Our team will
              register it and send you the invoice. You can follow it under My Domains.
            </span>
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Search again
            </Button>
            <Link
              to={paths.client.domains}
              className="inline-flex h-10 items-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white transition-[filter] hover:brightness-110"
            >
              Go to My Domains
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          <div className="rounded-xl border border-slate-200 p-4">
            <DomainName domain={result.domain} extension={result.extension} large />
            <p className="mt-1 text-sm text-slate-600">{formatMoney(result.price)} per year</p>
          </div>

          <fieldset>
            <legend className="text-sm font-medium text-slate-900">For how long?</legend>
            <div className="mt-2 grid grid-cols-5 gap-2">
              {[1, 2, 3, 4, 5].map((y) => (
                <button
                  key={y}
                  type="button"
                  aria-pressed={years === y}
                  onClick={() => setYears(y)}
                  className={cn(
                    'h-11 rounded-lg border text-sm font-semibold transition-colors',
                    years === y
                      ? 'border-brand-500 bg-brand-500/10 text-slate-900 ring-1 ring-brand-500/40'
                      : 'border-slate-200 text-slate-600 hover:border-brand-400/60',
                  )}
                >
                  {y} yr{y > 1 ? 's' : ''}
                </button>
              ))}
            </div>
          </fieldset>

          <div className="flex items-center justify-between border-t border-slate-200 pt-4">
            <span className="text-sm text-slate-600">Total</span>
            <span className="text-xl font-bold text-slate-900">{formatMoney(total)}</span>
          </div>

          <ul className="space-y-1.5 text-sm text-slate-600">
            <li>• Nothing is charged now. We register the domain and send you an invoice.</li>
            <li>• We confirm the final availability when we register it.</li>
            <li>• You can connect it to WAMUGII hosting or any other service.</li>
          </ul>

          {error && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {error.message}
            </p>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={() => order.mutate()} isLoading={order.isPending}>
              Request {result.domain}
            </Button>
          </div>
        </div>
      )}
    </Modal>
  )
}
