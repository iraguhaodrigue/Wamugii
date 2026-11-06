import { Suspense } from 'react'
import { useQuery } from '@tanstack/react-query'
import { listServices } from '@/api/services'
import { lazyDefault } from '@/lib/lazyPage'
import { Hero } from '@/components/home/Hero'
import { CapabilityChips } from '@/components/home/CapabilityChips'
import { MetricCards } from '@/components/home/MetricCards'

// Everything below the first screen loads as a separate file, so the hero
// appears sooner; the rest streams in while the visitor reads it.
const HomeBelowFold = lazyDefault(() => import('@/components/home/HomeBelowFold'))

/**
 * The homepage is a composition of section components (src/components/home).
 * One services query is fetched here and passed down, so the explorer, chips,
 * grid, metrics and deep-dive links all read from the same live response
 * rather than each firing their own request.
 */
export function Home() {
  const { data: services, isLoading, isError, refetch } = useQuery({
    queryKey: ['services', 'home-preview'],
    queryFn: () => listServices(),
  })

  const list = services ?? []

  return (
    <>
      <Hero services={list} isLoading={isLoading} />
      <CapabilityChips services={list} isLoading={isLoading} />
      <MetricCards serviceCount={list.length} />
      <Suspense fallback={<div className="min-h-[60vh]" aria-hidden="true" />}>
        <HomeBelowFold services={services} list={list} isLoading={isLoading} isError={isError} onRetry={() => refetch()} />
      </Suspense>
    </>
  )
}
