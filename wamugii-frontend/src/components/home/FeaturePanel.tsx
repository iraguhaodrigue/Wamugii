import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'

const stages = ['Planning', 'Design', 'Development', 'Deployment', 'Support']

export function FeaturePanel() {
  return (
    <section className="relative py-20 sm:py-24">
      <Container>
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl border border-brand-400/20 bg-[var(--color-brand-950)] p-8 shadow-[var(--shadow-glow-brand)] sm:p-12 lg:p-16">
            <AnimatedTechBackground intensity="cta" />
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  'radial-gradient(700px circle at 10% 0%, rgb(6 182 212 / 22%), transparent 60%), radial-gradient(700px circle at 95% 100%, rgb(124 58 237 / 22%), transparent 60%)',
              }}
              aria-hidden="true"
            />

            <div className="relative mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                From idea to <span className="text-gradient-brand">working technology</span>
              </h2>
              <p className="mt-4 text-base leading-relaxed text-slate-400">
                You don't need separate people for the plan, the build, the launch and the upkeep. WAMUGII covers the
                whole path — so there's one team accountable for the result instead of a chain of handovers.
              </p>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                {stages.map((stage, index) => (
                  <span
                    key={stage}
                    className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-slate-400 backdrop-blur-sm"
                  >
                    <span className="size-1.5 rounded-full bg-brand-400" aria-hidden="true" />
                    {stage}
                    {index < stages.length - 1 && (
                      <ArrowRight className="ml-1 size-3 text-slate-500" aria-hidden="true" />
                    )}
                  </span>
                ))}
              </div>

              <Link
                to={paths.requestQuote}
                className="mt-9 inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)]"
              >
                Start your project
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
