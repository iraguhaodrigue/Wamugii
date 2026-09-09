import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2, Code2, Globe, Server, Wrench } from 'lucide-react'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'
import { SectionHeading } from './SectionHeading'

/**
 * Each entry mirrors a real service in the catalogue. `match` is used to find
 * that service in the live API response so the CTA deep-links to its actual
 * detail page; if the service isn't published, the link falls back to the
 * services index rather than pointing at a page that doesn't exist.
 */
const deepDives = [
  {
    match: 'web design',
    icon: Globe,
    name: 'Web Design & Development',
    promise: 'Give your business a professional digital presence.',
    description:
      'A website that represents your business properly — quick to load, readable on a phone, and simple enough that your team can keep it current.',
    points: ['Responsive business websites', 'Landing & corporate sites', 'E-commerce storefronts', 'Ongoing maintenance'],
  },
  {
    match: 'software development',
    icon: Code2,
    name: 'Software Development',
    promise: 'Software shaped around how your business actually works.',
    description:
      'When spreadsheets and off-the-shelf tools stop fitting, we build the system that does — with your process, your rules and your data at the centre of it.',
    points: ['Custom business systems', 'Internal tools & dashboards', 'Process automation', 'Integration between systems'],
  },
  {
    match: 'consultancy',
    icon: Wrench,
    name: 'IT Consultancy',
    promise: 'Know what to fix before you spend money on it.',
    description:
      'An honest review of what you have, what is holding you back, and what is genuinely worth investing in next — advice first, not a sales pitch.',
    points: ['Systems review', 'Technology recommendations', 'Planning & budget guidance', 'Migration planning'],
  },
  {
    match: 'hosting',
    icon: Server,
    name: 'Hosting & Domains',
    promise: 'Somewhere reliable for your business to live online.',
    description:
      'Domains, hosting and the configuration around them — set up correctly once, then looked after so renewals and outages are not your problem.',
    points: ['Domain registration & setup', 'Website & application hosting', 'Email configuration', 'Backups & renewals'],
  },
]

export interface ServiceDeepDiveProps {
  services: Service[]
}

export function ServiceDeepDive({ services }: ServiceDeepDiveProps) {
  function linkFor(match: string): string {
    const found = services.find((service) => service.name.toLowerCase().includes(match))
    return found ? paths.serviceDetail(found.id) : paths.services
  }

  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <div className="glow-pool-teal pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <SectionHeading
          label="Services in detail"
          title="What each service actually gives you"
          description="The same services, explained in terms of the problem they solve rather than the technology behind them."
        />

        <div className="mt-16 space-y-14 sm:space-y-20">
          {deepDives.map(({ match, icon: Icon, name, promise, description, points }, index) => {
            const isReversed = index % 2 === 1
            return (
              <Reveal key={name}>
                <div className="grid items-center gap-8 lg:grid-cols-2 lg:gap-14">
                  <div className={cn(isReversed && 'lg:order-2')}>
                    <div className="flex size-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-500/15 text-brand-400 ring-1 ring-inset ring-brand-400/20">
                      <Icon className="size-5" aria-hidden="true" />
                    </div>
                    <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-brand-400">{name}</p>
                    <h3 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">{promise}</h3>
                    <p className="mt-3.5 text-base leading-relaxed text-slate-500">{description}</p>
                    <Link
                      to={linkFor(match)}
                      className="mt-6 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
                    >
                      Explore service
                      <ArrowRight className="size-4" aria-hidden="true" />
                    </Link>
                  </div>

                  <div className={cn(isReversed && 'lg:order-1')}>
                    <div className="rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-7">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">What's included</p>
                      <ul className="mt-4 space-y-3">
                        {points.map((point, pointIndex) => (
                          <li key={point}>
                            <Reveal delay={pointIndex * 60}>
                              <div className="flex items-start gap-3 rounded-lg border border-white/5 bg-white/[0.03] px-3.5 py-3">
                                <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-400" aria-hidden="true" />
                                <span className="text-sm text-slate-500">{point}</span>
                              </div>
                            </Reveal>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </Reveal>
            )
          })}
        </div>
      </Container>
    </section>
  )
}
