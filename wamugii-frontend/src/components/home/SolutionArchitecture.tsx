import { Cloud, Database, Headset, LayoutGrid, ShieldCheck } from 'lucide-react'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

const layers = [
  {
    icon: LayoutGrid,
    title: 'The part your customers see',
    detail: 'Website, storefront or portal — the public face of the business.',
  },
  {
    icon: Database,
    title: 'The part your team uses',
    detail: 'Internal systems that hold your records, orders and day-to-day work.',
  },
  {
    icon: Cloud,
    title: 'Where it all runs',
    detail: 'Hosting, domains and infrastructure, configured and maintained.',
  },
  {
    icon: ShieldCheck,
    title: 'What keeps it safe',
    detail: 'Access control, sensible data handling and secure defaults throughout.',
  },
  {
    icon: Headset,
    title: 'Who keeps it working',
    detail: 'Ongoing technical support once everything is live.',
  },
]

/**
 * The "how the pieces fit together" story. Rendered as a connected vertical
 * stack rather than another card grid, so this section reads differently from
 * the ones around it.
 */
export function SolutionArchitecture() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <div className="glow-pool-teal pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:items-center lg:gap-16">
          <div>
            <SectionHeading
              align="left"
              label="How it fits together"
              title="Five layers, one working system"
              description="Most businesses don't need one thing — they need a few things that talk to each other properly. We can build any single layer, or the whole stack."
            />
          </div>

          <div className="relative">
            <div
              className="absolute bottom-6 left-[22px] top-6 w-px bg-gradient-to-b from-brand-400/40 via-accent-400/30 to-transparent"
              aria-hidden="true"
            />
            <ul className="space-y-4">
              {layers.map(({ icon: Icon, title, detail }, index) => (
                <li key={title}>
                  <Reveal delay={index * 80}>
                    <div className="flex gap-4">
                      <div className="relative z-10 flex size-11 shrink-0 items-center justify-center rounded-xl border border-brand-400/20 bg-panel text-brand-400 backdrop-blur-sm">
                        <Icon className="size-5" aria-hidden="true" />
                      </div>
                      <div className="min-w-0 flex-1 rounded-xl border border-slate-200 bg-panel p-4 shadow-[var(--shadow-card)] backdrop-blur-sm transition-colors hover:border-brand-400/30">
                        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
                        <p className="mt-1 text-sm text-slate-500">{detail}</p>
                      </div>
                    </div>
                  </Reveal>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Container>
    </section>
  )
}
