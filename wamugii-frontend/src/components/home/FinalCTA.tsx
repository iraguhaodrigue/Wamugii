import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'

export function FinalCTA() {
  return (
    <section className="relative overflow-hidden bg-[var(--color-brand-950)] py-24 sm:py-32">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(900px circle at 15% 0%, rgb(6 182 212 / 26%), transparent 60%), radial-gradient(900px circle at 90% 100%, rgb(124 58 237 / 24%), transparent 60%)',
        }}
        aria-hidden="true"
      />
      <AnimatedTechBackground intensity="cta" />
      <Container className="relative">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-5xl">
              Have an idea? <span className="text-gradient-brand">Let's build it.</span>
            </h2>
            <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-slate-400">
              Tell us what your business needs and we'll help turn it into a practical digital solution — starting
              with an honest conversation about whether we're the right fit.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to={paths.requestQuote}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Request a Quote
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              <Link
                to={paths.services}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg border border-white/20 bg-white/5 px-6 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Explore Services
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
            <p className="mt-6 text-xs text-slate-500">No account needed to send a request.</p>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
