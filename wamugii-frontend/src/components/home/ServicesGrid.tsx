import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container, EmptyState, ErrorState } from '@/components/ui'
import { ServiceCard } from '@/components/services/ServiceCard'
import { ServiceCardSkeleton } from '@/components/services/ServiceCardSkeleton'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

export interface ServicesGridProps {
  services: Service[] | undefined
  isLoading: boolean
  isError: boolean
  onRetry: () => void
}

/** The live services grid — unchanged data flow, just lifted out of Home.tsx. */
export function ServicesGrid({ services, isLoading, isError, onRetry }: ServicesGridProps) {
  const preview = services?.slice(0, 6) ?? []

  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <AnimatedTechBackground intensity="medium" />
      <Container className="relative">
        <SectionHeading
          label="What we do"
          title="A focused set of services"
          description="Covering the full lifecycle of your technology needs — from the first build to long-term support."
        />

        <div className="mt-14">
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
              onRetry={onRetry}
            />
          )}

          {!isLoading && !isError && preview.length === 0 && (
            <EmptyState title="No services published yet" description="Check back soon — we're setting things up." />
          )}

          {!isLoading && !isError && preview.length > 0 && (
            <>
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {preview.map((service, index) => (
                  <Reveal key={service.id} delay={index * 60} className="h-full">
                    <ServiceCard service={service} />
                  </Reveal>
                ))}
              </div>
              {services && services.length > preview.length && (
                <Reveal>
                  <div className="mt-10 text-center">
                    <Link
                      to={paths.services}
                      className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
                    >
                      View all {services.length} services
                      <ArrowRight className="size-4" aria-hidden="true" />
                    </Link>
                  </div>
                </Reveal>
              )}
            </>
          )}
        </div>
      </Container>
    </section>
  )
}
