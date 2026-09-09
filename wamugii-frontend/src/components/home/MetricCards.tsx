import { Boxes, Layers, LifeBuoy, Workflow } from 'lucide-react'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'

export interface MetricCardsProps {
  /** Live count from the services API — the only numeric claim on this page. */
  serviceCount: number
}

/**
 * Deliberately capability statements rather than invented statistics: the app
 * has no verified project/client figures to quote, and inventing them would be
 * worse than saying nothing. The one number shown is the real published
 * service count, read from the API.
 */
export function MetricCards({ serviceCount }: MetricCardsProps) {
  const metrics = [
    {
      icon: Boxes,
      value: serviceCount > 0 ? String(serviceCount) : 'Full',
      label: 'Services offered',
      description: 'Covering web, software, IT, hosting and support.',
    },
    {
      icon: Workflow,
      value: 'End-to-end',
      label: 'Delivery',
      description: 'From first conversation through to launch and beyond.',
    },
    {
      icon: Layers,
      value: 'Custom',
      label: 'Built to fit',
      description: 'Solutions scoped around your business, not a template.',
    },
    {
      icon: LifeBuoy,
      value: 'Long-term',
      label: 'Technical support',
      description: "We stay available after launch — not a one-time handover.",
    },
  ]

  return (
    <section className="relative overflow-hidden py-16 sm:py-20">
      <div className="glow-pool-teal pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(({ icon: Icon, value, label, description }, index) => (
            <Reveal key={label} delay={index * 70}>
              <div className="h-full rounded-xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] backdrop-blur-sm transition-colors hover:border-brand-400/30">
                <div className="flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
                <p className="mt-4 text-2xl font-bold tracking-tight text-slate-900">{value}</p>
                <p className="mt-0.5 text-sm font-semibold text-brand-400">{label}</p>
                <p className="mt-2 text-sm text-slate-500">{description}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}
