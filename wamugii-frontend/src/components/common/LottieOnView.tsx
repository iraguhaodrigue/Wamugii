import { lazy, Suspense, useEffect, useRef, useState, type CSSProperties } from 'react'

// Split point: everything lottie-web lands in this chunk, fetched only when an
// animation first scrolls into view.
const LottiePlayer = lazy(() => import('./LottiePlayer'))

export interface LottieOnViewProps {
  /** Path to a Lottie JSON under `public/`, e.g. `/graphics/lottie/man-robot.json`. */
  src: string
  loop?: boolean
  className?: string
  style?: CSSProperties
  /** Describes the animation. Omit it for purely decorative art. */
  ariaLabel?: string
}

function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * A Lottie animation that costs nothing until it is scrolled to.
 *
 * Neither the animation JSON nor the engine is touched until the wrapper first
 * enters the viewport: the engine sits behind `lazy()`, and the player fetches
 * the JSON from `src`, so mounting the player is what starts both. Once
 * mounted it stays mounted, and playback follows visibility from there.
 *
 * The wrapper always renders at the size the caller gives it, so the box is
 * reserved before anything loads and content below never shifts. If the
 * animation fails to load, the wrapper is left empty rather than showing a
 * broken graphic.
 *
 * Under `prefers-reduced-motion: reduce` the animation still loads and shows
 * its final frame, stopped — never an empty box.
 */
export function LottieOnView({ src, loop = true, className, style, ariaLabel }: LottieOnViewProps) {
  const ref = useRef<HTMLDivElement>(null)
  // Seeded during the first render rather than from the effect: with no
  // observer support the animation loads immediately instead of never showing.
  const [shouldLoad, setShouldLoad] = useState(() => typeof IntersectionObserver === 'undefined')
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (shouldLoad) return
    const el = ref.current
    if (!el) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          setShouldLoad(true)
          observer.disconnect()
        }
      },
      // Slightly early, so the chunk and the JSON are already in flight by the
      // time the animation is actually on screen.
      { rootMargin: '200px 0px' },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [shouldLoad])

  return (
    <div
      ref={ref}
      className={className}
      style={style}
      role={ariaLabel ? 'img' : undefined}
      aria-label={ariaLabel}
      aria-hidden={ariaLabel ? undefined : true}
    >
      {shouldLoad && !failed && (
        <Suspense fallback={null}>
          <LottiePlayer
            src={src}
            loop={loop}
            reduceMotion={prefersReducedMotion()}
            onError={() => setFailed(true)}
          />
        </Suspense>
      )}
    </div>
  )
}
