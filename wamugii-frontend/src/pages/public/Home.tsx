import { useQuery } from '@tanstack/react-query'
import { listServices } from '@/api/services'
import { Hero } from '@/components/home/Hero'
import { CapabilityChips } from '@/components/home/CapabilityChips'
import { MetricCards } from '@/components/home/MetricCards'
import { ServicesGrid } from '@/components/home/ServicesGrid'
import { ProcessSection } from '@/components/home/ProcessSection'
import { SolutionShowcase } from '@/components/home/SolutionShowcase'
import { FeaturePanel } from '@/components/home/FeaturePanel'
import { SolutionArchitecture } from '@/components/home/SolutionArchitecture'
import { TechnologyPillars } from '@/components/home/TechnologyPillars'
import { TechnologyCapabilities } from '@/components/home/TechnologyCapabilities'
import { ServiceDeepDive } from '@/components/home/ServiceDeepDive'
import { WhyWamugii } from '@/components/home/WhyWamugii'
import { ClientJourney } from '@/components/home/ClientJourney'
import { FaqSection } from '@/components/home/FaqSection'
import { FinalCTA } from '@/components/home/FinalCTA'

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
      <ServicesGrid services={services} isLoading={isLoading} isError={isError} onRetry={() => refetch()} />
      <ProcessSection />
      <SolutionShowcase />
      <FeaturePanel />
      <SolutionArchitecture />
      <TechnologyPillars />
      <TechnologyCapabilities />
      <ServiceDeepDive services={list} />
      <WhyWamugii />
      <ClientJourney />
      <FaqSection />
      <FinalCTA />
    </>
  )
}
