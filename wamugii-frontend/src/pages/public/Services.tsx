import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search } from 'lucide-react'
import { listServices } from '@/api/services'
import { Container, EmptyState, ErrorState, Input } from '@/components/ui'
import { ServiceCard } from '@/components/services/ServiceCard'
import { ServiceCardSkeleton } from '@/components/services/ServiceCardSkeleton'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'

export function Services() {
  const [search, setSearch] = useState('')

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
    if (!term) return services
    return services.filter(
      (service) =>
        service.name.toLowerCase().includes(term) ||
        service.short_description?.toLowerCase().includes(term) ||
        service.category?.toLowerCase().includes(term),
    )
  }, [services, search])

  return (
    <div className="relative overflow-hidden">
      <AnimatedTechBackground intensity="medium" />
      <Container className="relative py-16 sm:py-20">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Our Services</h1>
        <p className="mt-4 text-base text-slate-500">
          Everything we offer, from first build to long-term support. Pick a service to see the details, or request
          a quote directly.
        </p>
      </div>

      <div className="relative mx-auto mt-10 max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <Input
          type="search"
          placeholder="Search services…"
          aria-label="Search services"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

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
            {filtered.map((service) => (
              <ServiceCard key={service.id} service={service} />
            ))}
          </div>
        )}
      </div>
      </Container>
    </div>
  )
}
