import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { Reveal } from '@/components/common/Reveal'
import { ServiceExplorer } from './ServiceExplorer'

export interface HeroProps {
  services: Service[]
  isLoading?: boolean
}

export function Hero({ services, isLoading }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-[var(--color-brand-950)]">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            'radial-gradient(1200px circle at 20% -10%, rgb(6 182 212 / 30%), transparent 55%), radial-gradient(1000px circle at 100% 10%, rgb(124 58 237 / 25%), transparent 55%)',
        }}
        aria-hidden="true"
      />
      <AnimatedTechBackground intensity="hero" />
      <Container className="relative py-20 sm:py-28">
        <div className="mx-auto max-w-3xl text-center">
          <Reveal>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-brand-300 backdrop-blur-sm">
              <Sparkles className="size-3.5" aria-hidden="true" />
              Technology partner for growing businesses
            </span>
          </Reveal>

          <Reveal delay={80}>
            <h1 className="mt-6 text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
              We build the technology
              <br className="hidden sm:block" /> that <span className="text-gradient-brand">runs your business</span>
            </h1>
          </Reveal>

          <Reveal delay={150}>
            <p className="mt-5 text-lg font-medium text-brand-200 sm:text-xl">We Build. We Innovate. We Empower.</p>
            <p className="mx-auto mt-4 max-w-xl text-base text-slate-400">
              WAMUGII TECH SOLUTIONS designs, builds, and supports the software, websites, and IT systems that keep
              your business running — end to end.
            </p>
          </Reveal>

          <Reveal delay={220}>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to={paths.requestQuote}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Request a Quote
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              <Link
                to={paths.services}
                className="inline-flex h-12 w-full items-center justify-center rounded-lg border border-white/20 bg-white/5 px-6 text-sm font-semibold text-white backdrop-blur-sm transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Explore Services
              </Link>
            </div>
          </Reveal>

          <Reveal delay={300}>
            <ServiceExplorer services={services} isLoading={isLoading} />
          </Reveal>
        </div>
      </Container>
    </section>
  )
}
