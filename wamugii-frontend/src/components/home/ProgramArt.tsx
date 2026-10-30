/**
 * One small animated illustration per AI Program course, each showing the
 * course's core idea in motion:
 *
 *   career     — a chat: question, AI "typing", answer
 *   foundations— AI ⊃ ML ⊃ DL rings with orbiting signals
 *   mathpython — Python code typing beside a sine curve drawing itself
 *   ml         — data points appear, a regression line swings into best fit
 *   deep       — a 3×3 filter scans an image and lights a feature map
 *   llm        — a prompt, then tokens generated one by one
 *   deploy     — a shield check draws, data flows to live servers
 *
 * Pure SVG + CSS (`.pa-*` in index.css). Animations run only once the card
 * has revealed (`.reveal-in` ancestor) and never under reduced motion, where
 * each illustration shows its finished frame instead.
 */
export type ProgramArtKind = 'career' | 'foundations' | 'mathpython' | 'ml' | 'deep' | 'llm' | 'deploy'

const VB = '0 0 320 160'

function Career() {
  return (
    <svg viewBox={VB} className="h-full w-full">
      <g className="pa-pop" style={{ animationDelay: '0s' }}>
        <rect x="150" y="16" width="146" height="34" rx="12" fill="#22d3ee" fillOpacity="0.9" />
        <rect x="164" y="27" width="96" height="5" rx="2.5" fill="#052730" fillOpacity="0.75" />
        <rect x="164" y="36" width="64" height="5" rx="2.5" fill="#052730" fillOpacity="0.5" />
      </g>
      <g className="pa-pop" style={{ animationDelay: '0.7s' }}>
        <circle cx="38" cy="78" r="12" fill="url(#pa-career-av)" />
        <path d="M33 78l3 3 6-6" stroke="#fff" strokeWidth="2" fill="none" strokeLinecap="round" />
        <rect x="58" y="62" width="200" height="78" rx="14" fill="#fff" fillOpacity="0.08" stroke="#fff" strokeOpacity="0.14" />
      </g>
      <g className="pa-dots">
        {[0, 1, 2].map((i) => (
          <circle key={i} cx={78 + i * 12} cy="84" r="3.5" fill="#a5f3fc" className="pa-dot" style={{ animationDelay: `${i * 0.18}s` }} />
        ))}
      </g>
      {[0, 1, 2, 3].map((i) => (
        <rect
          key={i}
          x="72"
          y={76 + i * 14}
          width={[168, 150, 160, 96][i]}
          height="6"
          rx="3"
          fill={i === 0 ? '#67e8f9' : '#e2e8f0'}
          fillOpacity={i === 0 ? 0.9 : 0.55}
          className="pa-grow"
          style={{ animationDelay: `${2 + i * 0.35}s`, transformOrigin: '72px 0' }}
        />
      ))}
      <defs>
        <linearGradient id="pa-career-av" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#0e7490" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
    </svg>
  )
}

function Foundations() {
  const rings = [
    { r: 64, label: 'AI', color: '#a78bfa', speed: 'pa-spin-slow' },
    { r: 44, label: 'ML', color: '#22d3ee', speed: 'pa-spin-mid' },
    { r: 24, label: 'DL', color: '#f0abfc', speed: 'pa-spin-fast' },
  ]
  return (
    <svg viewBox={VB} className="h-full w-full">
      <circle cx="160" cy="80" r="74" fill="none" stroke="#a78bfa" strokeOpacity="0.25" strokeDasharray="3 7" className="pa-spin-rev" />
      {rings.map((ring) => (
        <g key={ring.label}>
          <circle cx="160" cy="80" r={ring.r} fill={ring.color} fillOpacity="0.07" stroke={ring.color} strokeOpacity="0.6" strokeWidth="1.5" />
          <g className={ring.speed}>
            <circle cx={160 + ring.r} cy="80" r="4" fill={ring.color} />
            <circle cx={160 + ring.r} cy="80" r="8" fill={ring.color} fillOpacity="0.25" />
          </g>
          <text x="160" y={80 - ring.r + 13} textAnchor="middle" fontSize="10" fontWeight="700" fill={ring.color}>
            {ring.label}
          </text>
        </g>
      ))}
      <circle cx="160" cy="80" r="5" fill="#fff" className="pa-breathe" />
    </svg>
  )
}

function MathPython() {
  const lines = [
    { t: 'import numpy as np', c: '#c4b5fd' },
    { t: 'x = np.linspace(0, 6)', c: '#e2e8f0' },
    { t: 'y = np.sin(x)', c: '#6ee7b7' },
    { t: 'plt.plot(x, y)', c: '#e2e8f0' },
  ]
  return (
    <svg viewBox={VB} className="h-full w-full">
      <rect x="12" y="20" width="150" height="120" rx="10" fill="#020617" fillOpacity="0.7" stroke="#fff" strokeOpacity="0.1" />
      {[0, 1, 2].map((i) => (
        <circle key={i} cx={24 + i * 9} cy="31" r="2.5" fill={['#f87171', '#fbbf24', '#34d399'][i]} />
      ))}
      {lines.map((l, i) => (
        <text
          key={i}
          x="22"
          y={56 + i * 20}
          fontSize="9.5"
          fontFamily="ui-monospace, Menlo, monospace"
          fill={l.c}
          className="pa-type"
          style={{ animationDelay: `${i * 0.6}s` }}
        >
          {l.t}
        </text>
      ))}
      <rect x="22" y="122" width="6" height="10" fill="#34d399" className="pa-blink" />
      <line x1="180" y1="80" x2="308" y2="80" stroke="#fff" strokeOpacity="0.25" />
      <line x1="184" y1="28" x2="184" y2="132" stroke="#fff" strokeOpacity="0.25" />
      <path
        d="M184 80 C200 40, 216 40, 230 80 S260 120, 276 80 S300 44, 308 56"
        fill="none"
        stroke="#34d399"
        strokeWidth="3"
        strokeLinecap="round"
        pathLength={100}
        className="pa-draw"
      />
      <text x="292" y="148" fontSize="10" fill="#6ee7b7" fontStyle="italic" textAnchor="end">
        y = sin(x)
      </text>
    </svg>
  )
}

function ML() {
  const pts = [
    [40, 122], [58, 112], [72, 118], [90, 98], [104, 104], [122, 86], [138, 90],
    [156, 72], [172, 78], [190, 60], [206, 64], [224, 48], [240, 52], [262, 36], [280, 40],
  ]
  return (
    <svg viewBox={VB} className="h-full w-full">
      <line x1="28" y1="136" x2="300" y2="136" stroke="#fff" strokeOpacity="0.25" />
      <line x1="28" y1="18" x2="28" y2="136" stroke="#fff" strokeOpacity="0.25" />
      {pts.map(([x, y], i) => {
        const fit = 128 - (x! - 30) * 0.36
        return (
          <line key={`e${i}`} x1={x} y1={y} x2={x} y2={fit} stroke="#f0abfc" strokeOpacity="0.55" strokeDasharray="2 2" className="pa-residual" />
        )
      })}
      <g className="pa-fit" style={{ transformOrigin: '160px 82px' }}>
        <line x1="30" y1="128" x2="292" y2="34" stroke="url(#pa-ml-line)" strokeWidth="3" strokeLinecap="round" />
      </g>
      {pts.map(([x, y], i) => (
        <circle
          key={i}
          cx={x}
          cy={y}
          r="4.5"
          fill="#a78bfa"
          stroke="#ede9fe"
          strokeWidth="1"
          className="pa-point"
          style={{ animationDelay: `${i * 0.08}s`, transformOrigin: `${x}px ${y}px` }}
        />
      ))}
      <defs>
        <linearGradient id="pa-ml-line" x1="0" x2="1">
          <stop offset="0" stopColor="#22d3ee" />
          <stop offset="1" stopColor="#f0abfc" />
        </linearGradient>
      </defs>
    </svg>
  )
}

// A rough "7" so the input reads as an image of a handwritten digit.
const DIGIT = [
  '001111', '000001', '000010', '000100', '001000', '010000',
]

function Deep() {
  const cell = 16
  const ox = 22
  const oy = 32
  return (
    <svg viewBox={VB} className="h-full w-full">
      {DIGIT.map((row, r) =>
        row.split('').map((v, c) => (
          <rect
            key={`${r}-${c}`}
            x={ox + c * cell}
            y={oy + r * cell}
            width={cell - 2}
            height={cell - 2}
            rx="2"
            fill={v === '1' ? '#f472b6' : '#fff'}
            fillOpacity={v === '1' ? 0.85 : 0.07}
          />
        )),
      )}
      <g className="pa-scan-y">
        <g className="pa-scan-x">
          <rect
            x={ox - 2}
            y={oy - 2}
            width={cell * 3 + 2}
            height={cell * 3 + 2}
            rx="4"
            fill="#f9a8d4"
            fillOpacity="0.12"
            stroke="#fbcfe8"
            strokeWidth="2"
          />
        </g>
      </g>
      <path d="M134 80h34m-8-6 8 6-8 6" stroke="#fbcfe8" strokeOpacity="0.6" strokeWidth="2" fill="none" />
      {Array.from({ length: 16 }).map((_, i) => (
        <rect
          key={i}
          x={186 + (i % 4) * 26}
          y={30 + Math.floor(i / 4) * 26}
          width="22"
          height="22"
          rx="4"
          fill="#f472b6"
          className="pa-feature"
          style={{ animationDelay: `${i * 0.5}s`, fillOpacity: [0.7, 0.9, 0.5, 0.3, 0.2, 0.4, 0.8, 0.2, 0.3, 0.8, 0.3, 0.1, 0.8, 0.3, 0.1, 0.1][i] }}
        />
      ))}
    </svg>
  )
}

function LLM() {
  const tokens = ['AI', 'learns', 'patterns', 'from', 'examples']
  let x = 22
  const placed = tokens.map((t) => {
    const w = t.length * 6 + 14
    const item = { t, x, w }
    x += w + 6
    return item
  })
  return (
    <svg viewBox={VB} className="h-full w-full">
      <rect x="14" y="16" width="292" height="30" rx="10" fill="#fff" fillOpacity="0.07" stroke="#fbbf24" strokeOpacity="0.45" />
      <text x="28" y="35" fontSize="10.5" fill="#fde68a">
        Prompt: Explain AI in one sentence
      </text>
      {placed.map((p, i) => (
        <g key={i} className="pa-token" style={{ animationDelay: `${0.5 + i * 0.45}s` }}>
          <rect x={p.x} y="62" width={p.w} height="22" rx="7" fill="#fbbf24" fillOpacity={0.14 + (i % 3) * 0.05} stroke="#fbbf24" strokeOpacity="0.6" />
          <text x={p.x + p.w / 2} y="77" fontSize="10" textAnchor="middle" fill="#fef3c7" fontWeight="600">
            {p.t}
          </text>
        </g>
      ))}
      <text x="22" y="110" fontSize="8.5" fill="#fde68a" fillOpacity="0.7">
        next word?
      </text>
      {[
        { w: 120, label: 'patterns' },
        { w: 54, label: 'rules' },
        { w: 28, label: 'magic' },
      ].map((b, i) => (
        <g key={b.label}>
          <rect x="70" y={101 + i * 15} width={b.w} height="9" rx="4.5" fill="#f59e0b" fillOpacity={0.85 - i * 0.25} className="pa-prob" style={{ animationDelay: `${i * 0.2}s`, transformOrigin: '70px 0' }} />
          <text x={76 + b.w} y={109 + i * 15} fontSize="8.5" fill="#fef3c7" fillOpacity="0.8">
            {b.label}
          </text>
        </g>
      ))}
    </svg>
  )
}

function Deploy() {
  return (
    <svg viewBox={VB} className="h-full w-full">
      <path
        d="M70 22 L112 38 V76 C112 104 92 124 70 136 C48 124 28 104 28 76 V38 Z"
        fill="#34d399"
        fillOpacity="0.1"
        stroke="#34d399"
        strokeWidth="2.5"
        strokeLinejoin="round"
        pathLength={100}
        className="pa-draw"
      />
      <path d="M52 78 l12 12 l22 -24" fill="none" stroke="#6ee7b7" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" pathLength={100} className="pa-check" />
      <path d="M124 80 H196" stroke="#34d399" strokeOpacity="0.7" strokeWidth="2.5" strokeDasharray="6 6" className="pa-flow" />
      {[0, 1, 2].map((i) => (
        <g key={i}>
          <rect x="206" y={30 + i * 36} width="98" height="28" rx="6" fill="#fff" fillOpacity="0.06" stroke="#fff" strokeOpacity="0.16" />
          {[0, 1, 2].map((j) => (
            <rect key={j} x={216 + j * 10} y={42 + i * 36} width="6" height="4" rx="1" fill="#94a3b8" fillOpacity="0.6" />
          ))}
          <circle cx="284" cy={44 + i * 36} r="4" fill="#34d399" className="pa-led" style={{ animationDelay: `${i * 0.4}s` }} />
          <circle cx="294" cy={44 + i * 36} r="4" fill="#22d3ee" className="pa-led" style={{ animationDelay: `${0.9 + i * 0.3}s` }} />
        </g>
      ))}
      <text x="255" y="150" fontSize="9" textAnchor="middle" fill="#6ee7b7" fontWeight="700" letterSpacing="1">
        LIVE
      </text>
    </svg>
  )
}

const ART: Record<ProgramArtKind, () => React.JSX.Element> = {
  career: Career,
  foundations: Foundations,
  mathpython: MathPython,
  ml: ML,
  deep: Deep,
  llm: LLM,
  deploy: Deploy,
}

export function ProgramArt({ kind }: { kind: ProgramArtKind }) {
  const Art = ART[kind]
  return (
    <div className="pa-art h-full w-full" aria-hidden="true">
      <Art />
    </div>
  )
}
