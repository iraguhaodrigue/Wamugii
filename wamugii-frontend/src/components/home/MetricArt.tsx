import { useEffect, useRef, useState, type CSSProperties, type JSX } from 'react'

/**
 * Small animated badges for the four metric cards under the hero, plus a
 * count-up for the one real number (the live service count). Each badge says
 * the card's idea in motion and none reuses a motif from elsewhere on the
 * page. Needs an <AnimInView> parent; reduced motion shows the final frame.
 */

const C = { cyan: '#22d3ee', violet: '#a78bfa', mint: '#34d399', amber: '#fbbf24' }

function a(cls: string, delay = 0, vars: Record<string, string> = {}, origin?: string) {
  const style: Record<string, string> = { animationDelay: `${delay}s`, ...vars }
  if (origin) style.transformOrigin = origin
  return { className: cls, style: style as CSSProperties }
}

/** "Services offered" — a 3×3 grid of service tiles switching on one by one. */
function ServiceTiles() {
  return (
    <svg viewBox="0 0 120 48" className="h-full w-full">
      {Array.from({ length: 9 }).map((_, i) => {
        const x = 34 + (i % 3) * 18
        const y = 2 + Math.floor(i / 3) * 15.5
        return (
          <g key={i}>
            <rect x={x} y={y} width="14" height="12" rx="3" fill="#fff" fillOpacity="0.08" />
            <rect x={x} y={y} width="14" height="12" rx="3" fill={i % 2 ? C.violet : C.cyan} {...a('mt-tile', i * 0.22)} />
          </g>
        )
      })}
    </svg>
  )
}

/** "End-to-end delivery" — a parcel travels the whole road from start to finish. */
function Road() {
  return (
    <svg viewBox="0 0 120 48" className="h-full w-full">
      <path d="M10 34 C 34 34, 40 12, 62 14 S 92 34, 110 26" stroke="#fff" strokeOpacity="0.15" strokeWidth="3" fill="none" strokeLinecap="round" />
      <path
        d="M10 34 C 34 34, 40 12, 62 14 S 92 34, 110 26"
        stroke={C.cyan}
        strokeWidth="3"
        fill="none"
        strokeLinecap="round"
        pathLength={100}
        {...a('mt-road')}
      />
      <circle cx="10" cy="34" r="4" fill={C.violet} />
      <g {...a('mt-flag')}>
        <path d="M110 26 V8" stroke={C.mint} strokeWidth="2" strokeLinecap="round" />
        <path d="M111 8h9l-3 4 3 4h-9z" fill={C.mint} />
      </g>
      <rect width="9" height="9" rx="2" fill={C.amber} {...a('mt-parcel')} style={{ offsetPath: "path('M10 34 C 34 34, 40 12, 62 14 S 92 34, 110 26')" } as CSSProperties} />
    </svg>
  )
}

/** "Built to fit" — three settings sliders move to a different setup each loop. */
function Sliders() {
  return (
    <svg viewBox="0 0 120 48" className="h-full w-full">
      {[0, 1, 2].map((i) => (
        <g key={i}>
          <rect x="20" y={8 + i * 15} width="90" height="3" rx="1.5" fill="#fff" fillOpacity="0.15" />
          <g {...a('mt-knob', i * 0.35, { '--k1': `${[10, 60, 30][i]}px`, '--k2': `${[70, 15, 80][i]}px`, '--k3': `${[40, 45, 55][i]}px` })}>
            <rect x="20" y={8 + i * 15} width="10" height="3" rx="1.5" fill={[C.cyan, C.violet, C.mint][i]} />
            <circle cx="25" cy={9.5 + i * 15} r="5" fill="#0f172a" stroke={[C.cyan, C.violet, C.mint][i]} strokeWidth="2.5" />
          </g>
        </g>
      ))}
    </svg>
  )
}

/** "Long-term support" — a 24/7 clock whose hand never stops. */
function Clock() {
  return (
    <svg viewBox="0 0 120 48" className="h-full w-full">
      <circle cx="92" cy="24" r="20" fill="#fff" fillOpacity="0.05" stroke={C.cyan} strokeWidth="2.5" />
      {Array.from({ length: 12 }).map((_, i) => (
        <line
          key={i}
          x1="92"
          y1="7"
          x2="92"
          y2={i % 3 === 0 ? 11 : 9.5}
          stroke="#fff"
          strokeOpacity="0.5"
          strokeWidth="1.5"
          transform={`rotate(${i * 30} 92 24)`}
        />
      ))}
      <g {...a('mt-hand-slow', 0, {}, '92px 24px')}>
        <path d="M92 24 V14" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" />
      </g>
      <g {...a('mt-hand-fast', 0, {}, '92px 24px')}>
        <path d="M92 24 V8" stroke={C.amber} strokeWidth="1.8" strokeLinecap="round" />
      </g>
      <circle cx="92" cy="24" r="2.5" fill={C.amber} />
      <text x="48" y="29" textAnchor="middle" fontSize="13" fontWeight="800" fill={C.cyan} {...a('mt-glow')}>
        24/7
      </text>
    </svg>
  )
}

const ART = { services: ServiceTiles, delivery: Road, custom: Sliders, support: Clock } satisfies Record<string, () => JSX.Element>
export type MetricKind = keyof typeof ART
export function MetricArt({ kind }: { kind: MetricKind }) {
  const Art = ART[kind]
  return <Art />
}

/** Counts from 0 up to `value` the first time it scrolls into view. */
export function CountUp({ value, durationMs = 1200 }: { value: number; durationMs?: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const reduce = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  const [shown, setShown] = useState(reduce ? value : 0)

  useEffect(() => {
    const el = ref.current
    if (!el || reduce || typeof IntersectionObserver === 'undefined') {
      setShown(value)
      return
    }
    let raf = 0
    const observer = new IntersectionObserver((entries) => {
      if (!entries[0]?.isIntersecting) return
      observer.disconnect()
      const start = performance.now()
      const tick = (now: number) => {
        const t = Math.min(1, (now - start) / durationMs)
        setShown(Math.round(value * (1 - Math.pow(1 - t, 3))))
        if (t < 1) raf = requestAnimationFrame(tick)
      }
      raf = requestAnimationFrame(tick)
    })
    observer.observe(el)
    return () => {
      observer.disconnect()
      cancelAnimationFrame(raf)
    }
  }, [value, durationMs, reduce])

  return (
    <span ref={ref} aria-label={String(value)}>
      {shown}
    </span>
  )
}
