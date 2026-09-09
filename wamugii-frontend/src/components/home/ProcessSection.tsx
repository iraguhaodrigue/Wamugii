import { Link } from 'react-router-dom'
import { ArrowRight, ClipboardList, Compass, LifeBuoy, Rocket } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

const steps = [
  {
    number: '01',
    icon: Compass,
    title: 'Discover',
    description:
      'We start with the business problem, not the technology. What is slowing you down, what needs to change, and what does success look like.',
  },
  {
    number: '02',
    icon: ClipboardList,
    title: 'Scope',
    description:
      'We define the solution, the features, the timeline and the budget — and you approve all of it before any work begins.',
  },
  {
    number: '03',
    icon: Rocket,
    title: 'Build & track',
    description:
      'We develop the solution in visible milestones. You follow progress and shared files in your own client portal as it happens.',
  },
  {
    number: '04',
    icon: LifeBuoy,
    title: 'Launch & support',
    description:
      'We deploy it, hand it over properly, and stay available for the changes, fixes and questions that come after launch.',
  },
]

export function ProcessSection() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <AnimatedTechBackground intensity="medium" />
      <Container className="relative">
        <SectionHeading
          label="How we work"
          title="A process you can actually follow"
          description="Four stages, no jargon, and nothing starts until you have agreed to it."
        />

        <div className="mt-14 grid gap-5 lg:grid-cols-2">
          {steps.map(({ number, icon: Icon, title, description }, index) => (
            <Reveal key={number} delay={index * 80}>
              <div className="group relative h-full overflow-hidden rounded-2xl border border-slate-200 bg-panel p-7 shadow-[var(--shadow-card)] backdrop-blur-sm transition-colors hover:border-brand-400/30 sm:p-8">
                <span
                  className="pointer-events-none absolute right-5 top-3 text-6xl font-bold leading-none text-brand-500/10 sm:text-7xl"
                  aria-hidden="true"
                >
                  {number}
                </span>
                <div className="relative flex size-12 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500/15 to-accent-500/15 text-brand-400 ring-1 ring-inset ring-brand-400/20">
                  <Icon className="size-6" aria-hidden="true" />
                </div>
                <p className="relative mt-5 text-xs font-semibold uppercase tracking-wider text-brand-400">
                  Step {number}
                </p>
                <h3 className="relative mt-1.5 text-xl font-semibold text-slate-900">{title}</h3>
                <p className="relative mt-2.5 text-sm leading-relaxed text-slate-500">{description}</p>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={120}>
          <div className="mt-10 text-center">
            <Link
              to={paths.requestQuote}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              Start at step one
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
