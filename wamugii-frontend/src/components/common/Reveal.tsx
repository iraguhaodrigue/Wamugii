import { useEffect, useRef, useState, type ReactNode } from 'react'
import { cn } from '@/utils/cn'

export interface RevealProps {
  children: ReactNode
  /** Stagger in ms — use increments of ~70ms across siblings in a grid. */
  delay?: number
  className?: string
}

/**
 * Reveals its children once, the first time they scroll into view. The
 * observer disconnects immediately after firing, so a long page costs one
 * short-lived observer per block rather than a persistent scroll listener.
 * Under `prefers-reduced-motion: reduce` the content is shown immediately and
 * the observer is never created (the CSS also neutralises the transition).
 */
function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function Reveal({ children, delay = 0, className }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null)
  // Seeded during the first render rather than set from the effect, so
  // reduced-motion users never get a hidden first paint.
  const [shown, setShown] = useState(prefersReducedMotion)

  useEffect(() => {
    const el = ref.current
    // Reduced motion is already resolved to `shown` above — no observer needed.
    if (!el || prefersReducedMotion()) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setShown(true)
          observer.disconnect()
        }
      },
      { threshold: 0.1, rootMargin: '0px 0px -48px 0px' },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      className={cn('reveal', shown && 'reveal-in', className)}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </div>
  )
}
