import { cn } from '@/utils/cn'

/**
 * An animated neural network drawn in SVG: signals flow along the links,
 * neurons pulse in waves from input to output, and three labelled chips float
 * around it. Pure CSS animation (see `.neural-*` in index.css), so it costs no
 * JavaScript and stops under `prefers-reduced-motion`.
 */
const LAYERS = [
  { x: 70, ys: [90, 170, 250, 330] },
  { x: 190, ys: [60, 140, 220, 300, 380] },
  { x: 310, ys: [100, 180, 260, 340] },
  { x: 430, ys: [160, 280] },
]

export interface NeuralArtProps {
  className?: string
  /** Show the three floating label chips. */
  chips?: boolean
}

export function NeuralArt({ className, chips = true }: NeuralArtProps) {
  const links: { x1: number; y1: number; x2: number; y2: number; i: number }[] = []
  let i = 0
  for (let l = 0; l < LAYERS.length - 1; l++) {
    const a = LAYERS[l]!
    const b = LAYERS[l + 1]!
    for (const y1 of a.ys) for (const y2 of b.ys) links.push({ x1: a.x, y1, x2: b.x, y2, i: i++ })
  }

  return (
    <div className={cn('relative', className)} aria-hidden="true">
      <svg viewBox="0 0 500 440" className="h-auto w-full" fill="none">
        <defs>
          <linearGradient id="neural-link" x1="0" x2="1">
            <stop offset="0" stopColor="#22d3ee" />
            <stop offset="1" stopColor="#a78bfa" />
          </linearGradient>
          <radialGradient id="neural-node">
            <stop offset="0" stopColor="#ecfeff" />
            <stop offset="0.45" stopColor="#22d3ee" />
            <stop offset="1" stopColor="#0e7490" />
          </radialGradient>
          <radialGradient id="neural-halo">
            <stop offset="0" stopColor="#22d3ee" stopOpacity="0.35" />
            <stop offset="1" stopColor="#22d3ee" stopOpacity="0" />
          </radialGradient>
        </defs>

        <circle cx="250" cy="220" r="210" fill="url(#neural-halo)" className="neural-breathe" />

        {links.map((k) => (
          <g key={k.i}>
            <line x1={k.x1} y1={k.y1} x2={k.x2} y2={k.y2} stroke="#67e8f9" strokeOpacity="0.12" strokeWidth="1" />
            <line
              x1={k.x1}
              y1={k.y1}
              x2={k.x2}
              y2={k.y2}
              stroke="url(#neural-link)"
              strokeWidth="1.6"
              strokeLinecap="round"
              className="neural-signal"
              style={{ animationDelay: `${(k.i * 137) % 2400}ms` }}
            />
          </g>
        ))}

        {LAYERS.map((layer, li) =>
          layer.ys.map((y, ni) => (
            <g key={`${li}-${ni}`}>
              <circle
                cx={layer.x}
                cy={y}
                r="15"
                fill="#22d3ee"
                fillOpacity="0.18"
                className="neural-ping"
                style={{ animationDelay: `${li * 420 + ni * 90}ms`, transformOrigin: `${layer.x}px ${y}px` }}
              />
              <circle cx={layer.x} cy={y} r={li === LAYERS.length - 1 ? 11 : 8} fill="url(#neural-node)" />
            </g>
          )),
        )}
      </svg>

      {chips && (
        <>
          <span className="neural-chip left-[2%] top-[6%]" style={{ animationDelay: '0s' }}>
            Learn patterns
          </span>
          <span className="neural-chip right-[0%] top-[30%]" style={{ animationDelay: '1.4s' }}>
            Write prompts
          </span>
          <span className="neural-chip bottom-[4%] left-[22%]" style={{ animationDelay: '2.6s' }}>
            Verify answers
          </span>
        </>
      )}
    </div>
  )
}
