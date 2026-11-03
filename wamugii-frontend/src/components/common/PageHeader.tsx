import type { ReactNode } from 'react'
import { Container } from '@/components/ui'
import { AnimatedTechBackground } from '@/components/common/AnimatedTechBackground'
import { cn } from '@/utils/cn'

export interface PageHeaderProps {
  eyebrow?: string
  /** The page title. `highlight` (if given) is drawn in the brand gradient after it. */
  title: string
  highlight?: string
  description?: ReactNode
  /** Right-hand illustration (hidden below `sm` when `artOnMobile` is false). */
  art?: ReactNode
  artOnMobile?: boolean
  /** Extra content under the description — a search box, back link, chips. */
  children?: ReactNode
  /** Content above the title (e.g. a back link). */
  top?: ReactNode
  className?: string
}

/**
 * The animated header band used at the top of the inner public pages
 * (Services, Hosting, Courses, Request a Quote, service detail). Always dark
 * — it carries its own `dark` scope — so it reads the same in both themes and
 * gives every page a consistent, moving first impression: drifting aurora,
 * the particle network, and a page-specific animated illustration.
 */
export function PageHeader({
  eyebrow,
  title,
  highlight,
  description,
  art,
  artOnMobile = false,
  children,
  top,
  className,
}: PageHeaderProps) {
  return (
    <section className={cn('dark relative overflow-hidden bg-[var(--color-brand-950)]', className)}>
      <div
        className="pointer-events-none absolute inset-0 bg-cover bg-top bg-no-repeat opacity-50"
        style={{ backgroundImage: "url('/graphics/gradient-blobs.svg')" }}
        aria-hidden="true"
      />
      <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
        <div className="hb-aurora hb-aurora-a" />
        <div className="hb-aurora hb-aurora-b" />
      </div>
      <AnimatedTechBackground intensity="medium" />
      <Container className="relative py-12 sm:py-16">
        {top && <div className="hero-in mb-6">{top}</div>}
        <div className={cn('grid items-center gap-10', art && 'lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)]')}>
          <div className={cn(!art && 'mx-auto max-w-2xl text-center')}>
            {eyebrow && (
              <span className="hero-in inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-300">
                {eyebrow}
              </span>
            )}
            <h1
              className="hero-in mt-4 text-4xl font-extrabold leading-[1.08] tracking-tight text-white sm:text-5xl"
              style={{ animationDelay: '80ms' }}
            >
              {title} {highlight && <span className="text-gradient-hero">{highlight}</span>}
            </h1>
            {description && (
              <p className="hero-in mt-4 max-w-xl text-base text-white/75 sm:text-lg" style={{ animationDelay: '160ms' }}>
                {description}
              </p>
            )}
            {children && (
              <div className="hero-in mt-7" style={{ animationDelay: '240ms' }}>
                {children}
              </div>
            )}
          </div>
          {art && (
            <div
              className={cn('hero-in mx-auto w-full max-w-md lg:max-w-lg', !artOnMobile && 'hidden sm:block')}
              style={{ animationDelay: '220ms' }}
            >
              {art}
            </div>
          )}
        </div>
      </Container>
    </section>
  )
}
