import type { Service } from '@/api/services'
import { CourseSpotlight } from '@/components/home/CourseSpotlight'
import { AIProgram } from '@/components/home/AIProgram'
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

interface Props {
  services: Service[] | undefined
  list: Service[]
  isLoading: boolean
  isError: boolean
  onRetry: () => void
}

/** The home page sections below the first screen (loaded on demand by Home.tsx). */
export default function HomeBelowFold({ services, list, isLoading, isError, onRetry }: Props) {
  return (
    <>
      <CourseSpotlight />
      <AIProgram />
      <ServicesGrid services={services} isLoading={isLoading} isError={isError} onRetry={onRetry} />
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
