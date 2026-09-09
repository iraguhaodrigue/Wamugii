import { Cpu, Layers, LifeBuoy, ShieldCheck } from 'lucide-react'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

const pillars = [
  {
    icon: Cpu,
    title: 'Built around your needs',
    description:
      'We scope every build around how your business actually works, rather than bending your process to fit an off-the-shelf product.',
    support: 'Requirements first, architecture second.',
  },
  {
    icon: ShieldCheck,
    title: 'Secure by design',
    description:
      'Access control and careful data handling are part of the build from the start, not a checklist someone runs at the end.',
    support: 'Authentication, permissions and safe defaults.',
  },
  {
    icon: Layers,
    title: 'Ready to scale',
    description:
      'Systems designed to handle your first users and your busiest day, so growth means adding capacity rather than starting over.',
    support: 'Maintainable foundations, room to extend.',
  },
  {
    icon: LifeBuoy,
    title: 'Supported beyond launch',
    description:
      'Software needs looking after. We stay reachable for the fixes, updates and questions that come up once real people are using it.',
    support: 'Ongoing technical support and maintenance.',
  },
]

export function TechnologyPillars() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <Container>
        <SectionHeading
          label="Our principles"
          title="What every WAMUGII build has in common"
          description="Different projects, same standards."
        />

        <div className="mt-14 grid gap-5 sm:grid-cols-2">
          {pillars.map(({ icon: Icon, title, description, support }, index) => (
            <Reveal key={title} delay={index * 80} className="h-full">
              <div className="group relative h-full overflow-hidden rounded-2xl border border-slate-200 bg-panel p-7 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/30 hover:shadow-[var(--shadow-glow-brand)] sm:p-8">
                <div
                  className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/40 to-transparent opacity-0 transition-opacity group-hover:opacity-100"
                  aria-hidden="true"
                />
                <div className="flex size-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-500/15 text-brand-400 ring-1 ring-inset ring-brand-400/20">
                  <Icon className="size-6" aria-hidden="true" />
                </div>
                <h3 className="mt-5 text-lg font-semibold text-slate-900">{title}</h3>
                <p className="mt-2.5 text-sm leading-relaxed text-slate-500">{description}</p>
                <p className="mt-4 border-t border-slate-200 pt-3 text-xs font-medium text-brand-400">{support}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </Container>
    </section>
  )
}
