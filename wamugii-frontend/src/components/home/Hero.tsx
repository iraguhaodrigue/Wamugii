import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import type { Service } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { ServiceExplorer } from './ServiceExplorer'

export interface HeroProps {
  services: Service[]
  isLoading?: boolean
}

/**
 * Two-column hero: copy and CTAs on the left, illustration on the right,
 * stacking to one column below `lg`.
 *
 * The entrance uses `.hero-in` keyframes with per-element delays rather than
 * the Reveal observer the lower sections use — the hero is on screen at first
 * paint, so there is nothing to observe, and keyframes avoid a frame of
 * invisible content while the observer attaches.
 */
export function Hero({ services, isLoading }: HeroProps) {
  return (
    <section className="relative overflow-hidden bg-[var(--color-brand-950)]">
      {/* Ambient teal/purple glow. Decorative only, so it is a background
          layer rather than an <img> — nothing to describe and no layout cost. */}
      <div
        className="pointer-events-none absolute inset-0 bg-cover bg-top bg-no-repeat opacity-55"
        style={{ backgroundImage: "url('/graphics/gradient-blobs.svg')" }}
        aria-hidden="true"
      />
      {/* Static CSS light source, above the blobs and below the content. */}
      <div className="hero-glow pointer-events-none absolute inset-0" aria-hidden="true" />
      <AnimatedTechBackground intensity="hero" />

      <Container className="relative py-20 sm:py-24 lg:py-28">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div className="text-center lg:text-left">
            <span
              className="hero-in inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-brand-300 backdrop-blur-sm"
              style={{ animationDelay: '0ms' }}
            >
              <Sparkles className="size-3.5" aria-hidden="true" />
              Technology partner for growing businesses
            </span>

            <h1
              className="hero-in mt-6 text-[2rem] font-extrabold leading-[1.05] tracking-tight text-white sm:text-5xl md:text-6xl lg:text-7xl"
              style={{ animationDelay: '90ms' }}
            >
              We Build. We Innovate.
              <br className="hidden sm:block" />{' '}
              <span className="text-gradient-hero">We Empower.</span>
            </h1>

            <p
              className="hero-in mx-auto mt-5 max-w-xl text-base text-slate-400 sm:text-lg lg:mx-0"
              style={{ animationDelay: '180ms' }}
            >
              WAMUGII TECH SOLUTIONS designs, builds, and supports the software, websites, and IT systems that keep
              your business running — end to end.
            </p>

            <div
              className="hero-in mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row lg:justify-start"
              style={{ animationDelay: '270ms' }}
            >
              <Link
                to={paths.requestQuote}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-6 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter,transform] duration-200 hover:-translate-y-0.5 hover:brightness-110 active:translate-y-0 active:brightness-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Request a Quote
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              <Link
                to={paths.services}
                className="inline-flex h-12 w-full items-center justify-center rounded-lg border border-white/20 bg-white/5 px-6 text-sm font-semibold text-white backdrop-blur-sm transition-[background-color,border-color,transform] duration-200 hover:-translate-y-0.5 hover:border-white/30 hover:bg-white/10 active:translate-y-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-brand-950)] sm:w-auto"
              >
                Explore Services
              </Link>
            </div>
          </div>

          {/* `width`/`height` are set so the box is reserved before the SVG
              lands — no layout shift. The drift sits on the <img> because the
              wrapper's entrance animates `transform` too. */}
          <div className="hero-in" style={{ animationDelay: '360ms' }}>
            <img
              src="/graphics/hero-illustration.svg"
              alt=""
              width={600}
              height={480}
              fetchPriority="high"
              decoding="async"
              className="hero-float mx-auto h-auto w-full max-w-lg lg:max-w-none"
            />
          </div>
        </div>

        <div className="hero-in" style={{ animationDelay: '450ms' }}>
          <ServiceExplorer services={services} isLoading={isLoading} />
        </div>
      </Container>
    </section>
  )
}
