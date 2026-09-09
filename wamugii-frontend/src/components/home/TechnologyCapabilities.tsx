import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle2 } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

const capabilities = [
  'Maintainable systems that are cheap to change later',
  'Secure architecture and careful handling of your data',
  'Infrastructure that scales with demand',
  'Modern, well-supported development tooling',
  'Reliable deployment and handover',
]

/*
 * The right-hand visual is an abstract representation of a system stack —
 * intentionally not a screenshot, since there is no public, verified client
 * work in the project to display and fabricating one would be dishonest.
 */
function StackVisual() {
  const layers = [
    { label: 'Interface', hint: 'What people use', width: 'w-full' },
    { label: 'Application', hint: 'Business logic', width: 'w-[92%]' },
    { label: 'Data', hint: 'Records & storage', width: 'w-[84%]' },
    { label: 'Infrastructure', hint: 'Hosting & network', width: 'w-[76%]' },
  ]

  return (
    <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-8">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(400px circle at 80% 0%, rgb(6 182 212 / 14%), transparent 60%), radial-gradient(400px circle at 10% 100%, rgb(124 58 237 / 14%), transparent 60%)',
        }}
        aria-hidden="true"
      />
      <div className="relative space-y-3">
        {layers.map(({ label, hint, width }, index) => (
          <Reveal key={label} delay={index * 90}>
            <div
              className={`${width} mx-auto rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 backdrop-blur-sm`}
            >
              <div className="flex items-center justify-between gap-3">
                <span className="text-sm font-semibold text-slate-900">{label}</span>
                <span className="text-xs text-slate-500">{hint}</span>
              </div>
              <div className="mt-2.5 flex gap-1">
                {Array.from({ length: 5 }).map((_, i) => (
                  <span
                    key={i}
                    className={`h-1 flex-1 rounded-full ${
                      i <= index ? 'bg-gradient-to-r from-brand-400/70 to-accent-400/50' : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
            </div>
          </Reveal>
        ))}
      </div>
      <p className="relative mt-5 text-center text-xs text-slate-500">
        Every layer we build, host, secure and support.
      </p>
    </div>
  )
}

export function TechnologyCapabilities() {
  return (
    <section className="relative overflow-hidden border-y border-slate-200 bg-black/30 py-20 sm:py-24">
      <div className="glow-pool-purple pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <SectionHeading
              align="left"
              label="Technology & Innovation"
              title="Engineering built for the long run"
              description="We invest in solid foundations — clean architecture, secure defaults, and infrastructure that scales — so what we build keeps paying off long after launch."
            />

            <ul className="mt-8 space-y-3">
              {capabilities.map((capability, index) => (
                <li key={capability}>
                  <Reveal delay={index * 60}>
                    <div className="flex items-start gap-3">
                      <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-brand-400" aria-hidden="true" />
                      <span className="text-sm text-slate-500">{capability}</span>
                    </div>
                  </Reveal>
                </li>
              ))}
            </ul>

            <Reveal delay={120}>
              <Link
                to={paths.requestQuote}
                className="mt-8 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-400 hover:text-brand-300"
              >
                Start a conversation
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </Reveal>
          </div>

          <Reveal delay={100}>
            <StackVisual />
          </Reveal>
        </div>
      </Container>
    </section>
  )
}
