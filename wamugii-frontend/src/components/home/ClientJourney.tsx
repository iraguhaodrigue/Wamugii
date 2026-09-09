import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

/**
 * Deliberately distinct from ProcessSection: that one covers how a project is
 * *delivered*, this one covers what happens in the days right after someone
 * submits the quote form — the part people hesitate over. Steps match the real
 * quote-request flow in the app (public form → review → conversation →
 * proposal → project with portal access).
 */
const journey = [
  {
    step: '01',
    title: 'You tell us what you need',
    detail: 'Fill in the quote form — no account required, and no obligation attached to it.',
  },
  {
    step: '02',
    title: 'We review your request',
    detail: 'A real person reads it and works out whether we are the right fit for what you are asking.',
  },
  {
    step: '03',
    title: 'We talk it through',
    detail: 'A conversation about the problem, the options, and what would genuinely work for your budget.',
  },
  {
    step: '04',
    title: 'You get a clear proposal',
    detail: 'Scope, timeline and cost written down plainly — yours to review with no pressure to accept.',
  },
  {
    step: '05',
    title: 'We start building',
    detail: 'Once you approve, your project is set up and you get portal access to follow it from day one.',
  },
]

export function ClientJourney() {
  return (
    <section className="relative overflow-hidden border-y border-slate-200 bg-black/30 py-20 sm:py-24">
      <div className="glow-pool-teal pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <SectionHeading
          label="What happens next"
          title="After you click “Request a Quote”"
          description="No black box, no pushy follow-ups — here is exactly what the next few days look like."
        />

        <ol className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-5 lg:gap-3">
          {journey.map(({ step, title, detail }, index) => (
            <li key={step}>
              <Reveal delay={index * 80} className="h-full">
                <div className="relative flex h-full flex-col rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm transition-colors hover:border-brand-400/30">
                  <div
                    className="absolute inset-x-5 top-0 h-px bg-gradient-to-r from-brand-400/50 to-accent-400/30"
                    aria-hidden="true"
                  />
                  <span className="text-2xl font-bold tracking-tight text-gradient-brand">{step}</span>
                  <h3 className="mt-3 text-sm font-semibold text-white">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{detail}</p>
                </div>
              </Reveal>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  )
}
