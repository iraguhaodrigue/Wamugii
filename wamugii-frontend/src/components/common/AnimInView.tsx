import { useEffect, useRef, useState, type ReactNode } from 'react'
import { cn } from '@/utils/cn'

/**
 * Adds `anim-live` to its wrapper only while it is on screen, so the looping
 * `.ba-*` illustration animations (index.css) run only where someone can see
 * them and restart each time the block scrolls back into view. Reduced-motion
 * users never get motion: those animations are declared inside a
 * `prefers-reduced-motion: no-preference` block.
 */
export function AnimInView({
  children,
  className,
  decorative = true,
}: {
  children: ReactNode
  className?: string
  /** Hide from screen readers (pure illustration). Set false when wrapping real content. */
  decorative?: boolean
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [live, setLive] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') return
    const observer = new IntersectionObserver((entries) => setLive(Boolean(entries[0]?.isIntersecting)), {
      rootMargin: '80px 0px',
    })
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  return (
    <div ref={ref} className={cn('ba-art', live && 'anim-live', className)} aria-hidden={decorative || undefined}>
      {children}
    </div>
  )
}
