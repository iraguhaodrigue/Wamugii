import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { listServices } from '@/api/services'
import { Container, EmptyState, ErrorState, Input } from '@/components/ui'
import { ServiceCard } from '@/components/services/ServiceCard'
import { ServiceCardSkeleton } from '@/components/services/ServiceCardSkeleton'
import { Reveal } from '@/components/common/Reveal'
import { PageHeader } from '@/components/common/PageHeader'
import { ServicesOrbit } from '@/components/common/PageArt'
import { cn } from '@/utils/cn'

export function Services() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string | null>(null)

  const {
    data: services,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['services', 'list'],
    queryFn: () => listServices(),
  })

  const filtered = useMemo(() => {
    if (!services) return []
    const term = search.trim().toLowerCase()
    return services.filter(
      (service) =>
        (!category || service.category === category) &&
        (!term ||
          service.name.toLowerCase().includes(term) ||
          service.short_description?.toLowerCase().includes(term) ||
          service.category?.toLowerCase().includes(term)),
    )
  }, [services, search, category])

  // Only categories that are actually in use become filter chips.
  const categories = useMemo(
    () => [...new Set((services ?? []).map((s) => s.category).filter((c): c is string => Boolean(c)))],
    [services],
  )

  return (
    <>
      <PageHeader
        eyebrow="What we do"
        title="Our"
        highlight="Services"
        description="Everything we offer, from the first build to long-term support. Pick a service to see the details, or request a quote directly."
        art={<ServicesOrbit />}
      >
        <div className="relative max-w-md">
          <Search className="pointer-events-none absolute left-3 top-1/2 z-10 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search services…"
            aria-label="Search services"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </PageHeader>
      <Container className="relative py-12 sm:py-16">
      {categories.length > 1 && (
        <div className="flex flex-wrap justify-center gap-2" role="group" aria-label="Filter by category">
          {[null, ...categories].map((c) => {
            const active = category === c
            return (
              <button
                key={c ?? 'all'}
                type="button"
                onClick={() => setCategory(c)}
                aria-pressed={active}
                className={cn(
                  'rounded-full border px-4 py-1.5 text-sm font-medium transition-all duration-300',
                  active
                    ? 'chip-pop border-transparent bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white shadow-[var(--shadow-glow-brand)]'
                    : 'border-slate-200 bg-panel text-slate-600 hover:-translate-y-0.5 hover:border-brand-400/40 hover:text-brand-600',
                )}
              >
                {c ?? 'All services'}
              </button>
            )
          })}
        </div>
      )}

      <div className="mt-10">
        {isLoading && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <ServiceCardSkeleton key={i} />
            ))}
          </div>
        )}

        {isError && !isLoading && (
          <ErrorState
            title="Couldn't load services"
            message="We had trouble reaching the server. Please try again."
            onRetry={() => refetch()}
          />
        )}

        {!isLoading && !isError && services && services.length === 0 && (
          <EmptyState title="No services published yet" description="Check back soon — we're setting things up." />
        )}

        {!isLoading && !isError && services && services.length > 0 && filtered.length === 0 && (
          <EmptyState title="No services match your search" description="Try a different keyword." />
        )}

        {!isLoading && !isError && filtered.length > 0 && (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((service, index) => (
              <Reveal key={`${category ?? 'all'}-${service.id}`} delay={(index % 3) * 80} className="h-full">
                <ServiceCard service={service} />
              </Reveal>
            ))}
          </div>
        )}
      </div>
      </Container>
    </>
  )
}
