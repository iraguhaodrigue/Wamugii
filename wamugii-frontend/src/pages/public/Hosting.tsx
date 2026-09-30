import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, Server } from 'lucide-react'
import { listHostingPlans, type HostingPlan } from '@/api/hosting'
import { paths } from '@/routes/paths'
import { Container, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { formatMoney } from '@/utils/format'

/** "3 websites, SSL, 50GB SSD" -> one bullet per item. */
function featureList(features: string): string[] {
  return features
    .split(',')
    .map((f) => f.trim())
    .filter(Boolean)
}

function PlanCard({ plan }: { plan: HostingPlan }) {
  const monthly = Number(plan.monthly_price)
  const yearly = Number(plan.yearly_price)
  // 12 monthly payments vs the yearly price — only shown when there really is
  // a saving, rather than asserting "2 months free" regardless of the numbers.
  const monthsSaved = monthly > 0 ? Math.round((monthly * 12 - yearly) / monthly) : 0

  return (
    <div className="flex h-full flex-col rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-colors hover:border-brand-400/30">
      <div className="flex size-11 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
        <Server className="size-5" aria-hidden="true" />
      </div>

      <h3 className="mt-4 text-lg font-semibold text-slate-900">{plan.name}</h3>
      {plan.description && <p className="mt-1 text-sm text-slate-500">{plan.description}</p>}

      <div className="mt-4">
        <p className="text-2xl font-bold tracking-tight text-slate-900">
          {formatMoney(plan.monthly_price)}
          <span className="text-sm font-normal text-slate-500"> /month</span>
        </p>
        <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-slate-500">
          <span>or {formatMoney(plan.yearly_price)} /year</span>
          {monthsSaved > 0 && (
            <span className="inline-flex items-center rounded-full bg-brand-500/15 px-2 py-0.5 text-xs font-medium text-brand-600 ring-1 ring-inset ring-brand-400/20">
              {monthsSaved} {monthsSaved === 1 ? 'month' : 'months'} free
            </span>
          )}
        </p>
      </div>

      <ul className="mt-5 flex-1 space-y-2">
        {featureList(plan.features).map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm text-slate-600">
            <Check className="mt-0.5 size-4 shrink-0 text-brand-400" aria-hidden="true" />
            {feature}
          </li>
        ))}
      </ul>

      <Link
        to={`${paths.requestQuote}?service=hosting&plan=${encodeURIComponent(plan.name)}`}
        className="mt-6 inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-5 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
      >
        Get Started
        <ArrowRight className="size-4" aria-hidden="true" />
      </Link>
    </div>
  )
}

export function Hosting() {
  const {
    data: plans,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['hosting', 'plans', 'public'], queryFn: () => listHostingPlans() })

  return (
    <section className="relative overflow-hidden py-16 sm:py-20">
      <AnimatedTechBackground intensity="medium" />
      <Container className="relative">
        <div className="mx-auto max-w-2xl text-center">
          <span className="text-sm font-semibold uppercase tracking-wide text-brand-400">
            Hosting
          </span>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Reliable hosting for your business
          </h1>
          <p className="mt-4 text-base text-slate-500">
            Fast, secure hosting we set up and look after for you — so your site stays online
            without you having to think about servers.
          </p>
        </div>

        <div className="mt-12">
          {isLoading && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-96 rounded-xl" />
              ))}
            </div>
          )}

          {isError && !isLoading && (
            <ErrorState
              title="Couldn't load hosting plans"
              message="We had trouble reaching the server. Please try again."
              onRetry={() => refetch()}
            />
          )}

          {!isLoading && !isError && (plans?.length ?? 0) === 0 && (
            <EmptyState
              icon={Server}
              title="No hosting plans published yet"
              description="Check back soon — we're setting things up."
            />
          )}

          {!isLoading && !isError && plans && plans.length > 0 && (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {plans.map((plan) => (
                <PlanCard key={plan.id} plan={plan} />
              ))}
            </div>
          )}
        </div>

        <p className="mt-10 text-center text-sm text-slate-500">
          Need something different?{' '}
          <Link to={paths.requestQuote} className="font-semibold text-brand-600 hover:text-brand-700">
            Tell us what you need
          </Link>{' '}
          and we&apos;ll put together a plan.
        </p>
      </Container>
    </section>
  )
}
