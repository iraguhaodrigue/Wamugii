import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, Server } from 'lucide-react'
import { listHostingPlans, type HostingPlan } from '@/api/hosting'
import { paths } from '@/routes/paths'
import { Container, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { PageHeader } from '@/components/common/PageHeader'
import { HostingArt } from '@/components/common/PageArt'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'

type Billing = 'monthly' | 'yearly'
import { formatMoney } from '@/utils/format'

/** "3 websites, SSL, 50GB SSD" -> one bullet per item. */
function featureList(features: string): string[] {
  return features
    .split(',')
    .map((f) => f.trim())
    .filter(Boolean)
}

function PlanCard({ plan, billing }: { plan: HostingPlan; billing: Billing }) {
  const monthly = Number(plan.monthly_price)
  const yearly = Number(plan.yearly_price)
  // 12 monthly payments vs the yearly price — only shown when there really is
  // a saving, rather than asserting "2 months free" regardless of the numbers.
  const monthsSaved = monthly > 0 ? Math.round((monthly * 12 - yearly) / monthly) : 0

  return (
    <div className="group relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all duration-300 hover:-translate-y-1.5 hover:border-brand-400/40 hover:shadow-[var(--shadow-glow-brand)]">
      <span
        className="absolute inset-x-0 top-0 h-1 origin-left scale-x-0 bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] transition-transform duration-500 group-hover:scale-x-100"
        aria-hidden="true"
      />
      <div className="icon-live flex size-11 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
        <Server className="size-5" aria-hidden="true" />
      </div>

      <h3 className="mt-4 text-lg font-semibold text-slate-900">{plan.name}</h3>
      {plan.description && <p className="mt-1 text-sm text-slate-500">{plan.description}</p>}

      <div className="mt-4">
        <p key={billing} className="price-swap text-2xl font-bold tracking-tight text-slate-900">
          {formatMoney(billing === 'monthly' ? plan.monthly_price : plan.yearly_price)}
          <span className="text-sm font-normal text-slate-500"> /{billing === 'monthly' ? 'month' : 'year'}</span>
        </p>
        <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-slate-500">
          <span>
            or {formatMoney(billing === 'monthly' ? plan.yearly_price : plan.monthly_price)} /
            {billing === 'monthly' ? 'year' : 'month'}
          </span>
          {monthsSaved > 0 && (
            <span className="inline-flex items-center rounded-full bg-brand-500/15 px-2 py-0.5 text-xs font-medium text-brand-600 ring-1 ring-inset ring-brand-400/20">
              {monthsSaved} {monthsSaved === 1 ? 'month' : 'months'} free
            </span>
          )}
        </p>
      </div>

      <ul className="mt-5 flex-1 space-y-2">
        {featureList(plan.features).map((feature) => (
          <li key={feature} className="flex items-start gap-2 text-sm text-slate-600 transition-transform duration-300 group-hover:translate-x-0.5">
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
  const [billing, setBilling] = useState<Billing>('monthly')

  return (
    <>
    <PageHeader
      eyebrow="Hosting & domains"
      title="Reliable hosting for"
      highlight="your business"
      description="Fast, secure hosting we set up and look after for you — so your site stays online without you having to think about servers."
      art={<HostingArt />}
    />
    <section className="relative overflow-hidden py-12 sm:py-16">
      <Container className="relative">
        {plans && plans.length > 0 && (
          <div className="flex justify-center">
            <div className="relative inline-flex rounded-full border border-slate-200 bg-panel p-1 shadow-[var(--shadow-card)]" role="group" aria-label="Billing period">
              <span
                className={cn(
                  'absolute inset-y-1 w-[calc(50%-4px)] rounded-full bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] shadow-[var(--shadow-glow-brand)] transition-transform duration-300',
                  billing === 'yearly' ? 'translate-x-full' : 'translate-x-0',
                )}
                aria-hidden="true"
              />
              {(['monthly', 'yearly'] as const).map((b) => (
                <button
                  key={b}
                  type="button"
                  aria-pressed={billing === b}
                  onClick={() => setBilling(b)}
                  className={cn(
                    'relative z-10 w-28 rounded-full px-4 py-2 text-sm font-semibold capitalize transition-colors duration-300',
                    billing === b ? 'text-white' : 'text-slate-600 hover:text-slate-900',
                  )}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>
        )}
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
              {plans.map((plan, index) => (
                <Reveal key={plan.id} delay={index * 80} className="h-full">
                  <PlanCard plan={plan} billing={billing} />
                </Reveal>
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
    </>
  )
}
