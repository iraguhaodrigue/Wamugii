import type { CSSProperties } from 'react'

/**
 * Extra motion behind the homepage hero, layered under the content:
 *
 *  * an aurora — three large soft colour fields drifting slowly,
 *  * tech glyphs (code, AI, cloud, data) rising and fading like bubbles,
 *  * an occasional shooting light crossing the sky.
 *
 * Pure CSS (`.hb-*` in index.css): no JavaScript, GPU-friendly
 * (transform/opacity only), purely decorative, and still under
 * `prefers-reduced-motion`, where only the static aurora remains.
 */
const GLYPHS: { t: string; x: number; y: number; d: number; s: number; dur: number }[] = [
  { t: '</>', x: 6, y: 78, d: 0, s: 1, dur: 14 },
  { t: 'AI', x: 16, y: 40, d: 3, s: 0.9, dur: 16 },
  { t: '{ }', x: 30, y: 88, d: 6, s: 1.1, dur: 15 },
  { t: '01', x: 44, y: 62, d: 1.5, s: 0.8, dur: 13 },
  { t: '☁', x: 54, y: 84, d: 8, s: 1.2, dur: 17 },
  { t: '⚙', x: 64, y: 30, d: 4, s: 1, dur: 15 },
  { t: 'λ', x: 74, y: 76, d: 9.5, s: 0.9, dur: 14 },
  { t: '#', x: 84, y: 50, d: 2.5, s: 0.85, dur: 16 },
  { t: '▲', x: 92, y: 86, d: 7, s: 0.8, dur: 13 },
  { t: '()', x: 24, y: 20, d: 11, s: 0.8, dur: 15 },
  { t: 'DB', x: 88, y: 18, d: 5.5, s: 0.8, dur: 14 },
]

export function HeroBackdrop() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="hb-aurora hb-aurora-a" />
      <div className="hb-aurora hb-aurora-b" />
      <div className="hb-aurora hb-aurora-c" />
      {GLYPHS.map((g, i) => (
        <span
          key={i}
          className="hb-glyph"
          style={
            {
              left: `${g.x}%`,
              top: `${g.y}%`,
              animationDelay: `${g.d}s`,
              animationDuration: `${g.dur}s`,
              fontSize: `${g.s * 1.25}rem`,
            } as CSSProperties
          }
        >
          {g.t}
        </span>
      ))}
      <span className="hb-star" style={{ top: '14%', left: '58%', animationDelay: '2s' }} />
      <span className="hb-star" style={{ top: '6%', left: '22%', animationDelay: '7.5s' }} />
      <span className="hb-star" style={{ top: '30%', left: '86%', animationDelay: '12s' }} />
    </div>
  )
}
