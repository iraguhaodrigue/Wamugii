import { Link } from 'react-router-dom'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container, Skeleton } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'

export interface CapabilityChipsProps {
  services: Service[]
  isLoading?: boolean
}

/**
 * Capability badges built from the real service catalogue rather than a
 * hardcoded list — each chip is a working link to that service's page, so the
 * row doubles as navigation and never drifts out of sync with the backend.
 */
export function CapabilityChips({ services, isLoading = false }: CapabilityChipsProps) {
  return (
    <section className="relative border-b border-slate-200 py-8">
      <Container>
        <div className="flex flex-wrap items-center justify-center gap-2.5">
          {isLoading
            ? Array.from({ length: 7 }).map((_, i) => <Skeleton key={i} className="h-8 w-32 rounded-full" />)
            : services.map((service, index) => (
                <Reveal key={service.id} delay={index * 40}>
                  <Link
                    to={paths.serviceDetail(service.id)}
                    className="inline-flex rounded-full border border-slate-200 bg-panel px-3.5 py-1.5 text-xs font-medium text-slate-500 backdrop-blur-sm transition-colors hover:border-brand-400/40 hover:text-brand-400"
                  >
                    {service.name}
                  </Link>
                </Reveal>
              ))}
        </div>
      </Container>
    </section>
  )
}
