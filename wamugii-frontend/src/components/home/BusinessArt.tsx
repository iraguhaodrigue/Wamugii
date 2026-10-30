import type { CSSProperties, JSX } from 'react'

/**
 * Animated illustrations for the homepage business sections:
 *
 *  * SolutionArt — the six "Technology built around your business" blocks
 *  * ProcessArt  — the four "A process you can actually follow" steps
 *  * ServiceArt  — one per service card, picked from the service's name
 *
 * Abstract motifs (no fake screenshots of client work), pure SVG animated by
 * the shared `.ba-*` classes in index.css. Wrap each in <AnimInView> so they
 * only move while visible; each class falls back to its finished frame under
 * reduced motion.
 */

type Vars = Record<string, string | number>

/** className + style for an animated element: delay in seconds, CSS vars. */
function anim(cls: string, delay = 0, vars: Vars = {}, origin?: string): { className: string; style: CSSProperties } {
  const style: Record<string, string | number> = { animationDelay: `${delay}s`, ...vars }
  if (origin) style.transformOrigin = origin
  return { className: cls, style: style as CSSProperties }
}

const C = { cyan: '#22d3ee', violet: '#a78bfa', mint: '#34d399', pink: '#f472b6', amber: '#fbbf24', white: '#ffffff' }

function Svg({ children, vb = '0 0 320 110' }: { children: React.ReactNode; vb?: string }) {
  return (
    <svg viewBox={vb} preserveAspectRatio="xMidYMid meet" className="h-full w-full" fill="none">
      {children}
    </svg>
  )
}

// ---------------------------------------------------------------------------
// Solutions
// ---------------------------------------------------------------------------

/** Website — the same page scrolling on a desktop and a phone. */
function SolWebsite() {
  const page = (w: number) => (
    <>
      <rect x="0" y="0" width={w} height="26" rx="3" fill={C.cyan} fillOpacity="0.35" />
      <rect x="6" y="8" width={w * 0.45} height="4" rx="2" fill="#fff" fillOpacity="0.8" />
      <rect x="6" y="16" width={w * 0.3} height="4" rx="2" fill="#fff" fillOpacity="0.45" />
      {[0, 1, 2].map((i) => (
        <rect key={i} x={i * (w / 3) + 1} y="32" width={w / 3 - 4} height="20" rx="3" fill="#fff" fillOpacity="0.1" />
      ))}
      {[0, 1, 2, 3].map((i) => (
        <rect key={`l${i}`} x="2" y={58 + i * 8} width={w * (0.9 - i * 0.12)} height="3.5" rx="1.75" fill="#fff" fillOpacity="0.14" />
      ))}
      <rect x="0" y="94" width={w} height="22" rx="3" fill={C.violet} fillOpacity="0.3" />
      <rect x="6" y="122" width={w * 0.6} height="4" rx="2" fill="#fff" fillOpacity="0.2" />
    </>
  )
  return (
    <Svg>
      <defs>
        <clipPath id="sw-desk">
          <rect x="18" y="18" width="184" height="80" />
        </clipPath>
        <clipPath id="sw-phone">
          <rect x="240" y="20" width="52" height="78" />
        </clipPath>
      </defs>
      <rect x="12" y="4" width="196" height="100" rx="8" fill="#000" fillOpacity="0.3" stroke="#fff" strokeOpacity="0.14" />
      {[0, 1, 2].map((i) => (
        <circle key={i} cx={22 + i * 8} cy="11" r="2.2" fill={[C.cyan, C.violet, '#fff'][i]} fillOpacity="0.6" />
      ))}
      <g clipPath="url(#sw-desk)">
        <g transform="translate(18 18)">
          <g {...anim('ba-scroll', 0, { '--ty': '-42px', '--d': '7s' })}>{page(184)}</g>
        </g>
      </g>
      <rect x="234" y="6" width="64" height="100" rx="12" fill="#000" fillOpacity="0.35" stroke="#fff" strokeOpacity="0.18" />
      <rect x="256" y="11" width="20" height="3" rx="1.5" fill="#fff" fillOpacity="0.25" />
      <g clipPath="url(#sw-phone)">
        <g transform="translate(240 20)">
          <g {...anim('ba-scroll', 0.4, { '--ty': '-46px', '--d': '7s' })}>{page(52)}</g>
        </g>
      </g>
    </Svg>
  )
}

/** Management system — records arrive, statuses flip to done, a chart fills. */
function SolManagement() {
  return (
    <Svg>
      <rect x="8" y="6" width="210" height="98" rx="8" fill="#000" fillOpacity="0.3" stroke="#fff" strokeOpacity="0.12" />
      <rect x="18" y="14" width="190" height="10" rx="3" fill={C.cyan} fillOpacity="0.25" />
      {[0, 1, 2, 3, 4].map((i) => (
        <g key={i} {...anim('ba-pop', i * 0.35, { '--d': '7s' })}>
          <rect x="18" y={30 + i * 14} width="70" height="5" rx="2.5" fill="#fff" fillOpacity="0.35" />
          <rect x="98" y={30 + i * 14} width="40" height="5" rx="2.5" fill="#fff" fillOpacity="0.15" />
          <rect x="160" y={27.5 + i * 14} width="40" height="10" rx="5" fill="#fff" fillOpacity="0.12" />
          <rect x="160" y={27.5 + i * 14} width="40" height="10" rx="5" fill={C.mint} fillOpacity="0.75" {...anim('ba-pop', 2 + i * 0.4, { '--d': '7s' })} />
        </g>
      ))}
      <circle cx="268" cy="55" r="32" stroke="#fff" strokeOpacity="0.1" strokeWidth="10" />
      <circle
        cx="268"
        cy="55"
        r="32"
        stroke={C.violet}
        strokeWidth="10"
        strokeLinecap="round"
        pathLength={139}
        transform="rotate(-90 268 55)"
        {...anim('ba-draw', 0.6, { '--d': '7s' })}
      />
      <text x="268" y="59" textAnchor="middle" fontSize="12" fontWeight="700" fill="#fff">
        72%
      </text>
    </Svg>
  )
}

/** E-commerce — a product is picked, flies into the cart, badge pops. */
function SolShop() {
  return (
    <Svg>
      {Array.from({ length: 6 }).map((_, i) => {
        const x = 12 + (i % 3) * 62
        const y = 8 + Math.floor(i / 3) * 50
        return (
          <g key={i}>
            <rect x={x} y={y} width="56" height="44" rx="6" fill="#fff" fillOpacity="0.07" stroke="#fff" strokeOpacity="0.1" />
            <rect x={x + 6} y={y + 6} width="44" height="22" rx="4" fill={i === 1 ? C.cyan : '#fff'} fillOpacity={i === 1 ? 0.45 : 0.1} />
            <rect x={x + 6} y={y + 33} width="26" height="4" rx="2" fill="#fff" fillOpacity="0.35" />
            <rect x={x + 38} y={y + 32} width="12" height="6" rx="3" fill={C.violet} fillOpacity="0.6" />
          </g>
        )
      })}
      <rect x="72" y="6" width="60" height="48" rx="8" stroke={C.cyan} strokeWidth="2" {...anim('ba-pop', 0, { '--d': '5s' })} />
      <rect x="93" y="20" width="18" height="14" rx="3" fill={C.cyan} {...anim('ba-move', 0.4, { '--tx': '178px', '--ty': '26px', '--tx2': '178px', '--ty2': '26px', '--d': '5s' })} />
      <g transform="translate(250 34)">
        <path d="M0 6h8l7 26h28l6-18H12" stroke="#fff" strokeOpacity="0.8" strokeWidth="3" strokeLinejoin="round" strokeLinecap="round" />
        <circle cx="18" cy="40" r="4" fill="#fff" fillOpacity="0.8" />
        <circle cx="38" cy="40" r="4" fill="#fff" fillOpacity="0.8" />
        <g {...anim('ba-pop', 2.1, { '--d': '5s' })}>
          <circle cx="50" cy="2" r="10" fill={C.pink} />
          <text x="50" y="6" textAnchor="middle" fontSize="11" fontWeight="800" fill="#fff">
            1
          </text>
        </g>
      </g>
    </Svg>
  )
}

/** Automation — a form goes through a spinning gear into the database. */
function SolAutomation() {
  const nodes = [30, 120, 210, 290]
  return (
    <Svg>
      <path d="M48 55H272" stroke="#fff" strokeOpacity="0.12" strokeWidth="3" />
      <path d="M48 55H272" stroke={C.cyan} strokeWidth="3" strokeDasharray="6 10" {...anim('ba-flow', 0, { '--d': '0.8s', '--dash-end': -16 })} />
      {/* form */}
      <g>
        <rect x={nodes[0]! - 18} y="33" width="36" height="44" rx="5" fill="#0b2530" stroke={C.cyan} strokeOpacity="0.6" />
        {[0, 1, 2].map((i) => (
          <rect key={i} x={nodes[0]! - 11} y={43 + i * 9} width={22 - i * 5} height="4" rx="2" fill="#fff" fillOpacity="0.5" />
        ))}
      </g>
      {/* gear */}
      <g {...anim('ba-spin', 0, { '--d': '6s' }, `${nodes[1]}px 55px`)}>
        <circle cx={nodes[1]} cy="55" r="18" fill="#1c1636" stroke={C.violet} strokeWidth="7" strokeDasharray="6 5" />
        <circle cx={nodes[1]} cy="55" r="7" fill={C.violet} />
      </g>
      {/* database */}
      <g>
        <ellipse cx={nodes[2]} cy="38" rx="18" ry="6" fill="#0b2530" stroke={C.cyan} strokeOpacity="0.7" />
        <path d={`M${nodes[2]! - 18} 38v32c0 3.3 8 6 18 6s18-2.7 18-6V38`} fill="#0b2530" stroke={C.cyan} strokeOpacity="0.7" />
        <path d={`M${nodes[2]! - 18} 54c0 3.3 8 6 18 6s18-2.7 18-6`} stroke={C.cyan} strokeOpacity="0.5" />
      </g>
      {/* done */}
      <circle cx={nodes[3]} cy="55" r="16" fill={C.mint} fillOpacity="0.25" {...anim('ba-ping', 2.4, { '--d': '3s' }, `${nodes[3]}px 55px`)} />
      <circle cx={nodes[3]} cy="55" r="14" fill={C.mint} />
      <path d={`M${nodes[3]! - 6} 55l4 4 8-9`} stroke="#04261a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" pathLength={100} {...anim('ba-draw', 0.5, { '--d': '3s' })} />
      <circle cx="52" cy="55" r="5" fill="#fff" {...anim('ba-move', 0, { '--tx': '110px', '--ty': '0px', '--tx2': '216px', '--ty2': '0px', '--d': '3s' })} />
    </Svg>
  )
}

/** Hosting — a stack of servers with blinking status lights and an uptime line. */
function SolHosting() {
  return (
    <Svg>
      {[0, 1, 2].map((i) => (
        <g key={i}>
          <rect x="14" y={8 + i * 32} width="120" height="26" rx="6" fill="#fff" fillOpacity="0.07" stroke="#fff" strokeOpacity="0.14" />
          {[0, 1, 2, 3].map((j) => (
            <rect key={j} x={24 + j * 9} y={18 + i * 32} width="5" height="6" rx="1" fill="#94a3b8" fillOpacity="0.5" />
          ))}
          <rect x="66" y={19 + i * 32} width="34" height="4" rx="2" fill="#fff" fillOpacity="0.12" />
          <rect x="66" y={19 + i * 32} width="34" height="4" rx="2" fill={C.cyan} {...anim('ba-grow', i * 0.5, { '--d': '3.5s' }, `66px ${21 + i * 32}px`)} />
          <circle cx="114" cy={21 + i * 32} r="4" fill={C.mint} {...anim('ba-blink', i * 0.3)} />
          <circle cx="124" cy={21 + i * 32} r="4" fill={C.cyan} {...anim('ba-blink', 0.7 + i * 0.25, { '--d': '0.9s' })} />
        </g>
      ))}
      <rect x="150" y="8" width="160" height="90" rx="8" fill="#000" fillOpacity="0.3" stroke="#fff" strokeOpacity="0.12" />
      <text x="162" y="26" fontSize="9" fill="#94a3b8">
        Uptime
      </text>
      <text x="298" y="27" fontSize="12" fontWeight="800" textAnchor="end" fill={C.mint}>
        99.9%
      </text>
      <path
        d="M162 76 L180 70 L196 74 L212 62 L228 66 L244 52 L260 58 L276 44 L298 40"
        stroke={C.mint}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={100}
        {...anim('ba-draw', 0, { '--d': '5s' })}
      />
      <path d="M162 86H298" stroke="#fff" strokeOpacity="0.15" />
    </Svg>
  )
}

/** IT infrastructure — signals pulse from the core switch out to each device. */
function SolNetwork() {
  const core = { x: 160, y: 55 }
  const nodes = [
    { x: 40, y: 22 }, { x: 40, y: 88 }, { x: 110, y: 96 }, { x: 210, y: 96 }, { x: 280, y: 22 }, { x: 280, y: 88 }, { x: 160, y: 12 },
  ]
  return (
    <Svg>
      {nodes.map((n, i) => (
        <line key={i} x1={core.x} y1={core.y} x2={n.x} y2={n.y} stroke={i % 2 ? C.violet : C.cyan} strokeOpacity="0.35" strokeWidth="1.5" />
      ))}
      {nodes.map((n, i) => (
        <circle
          key={`p${i}`}
          cx={core.x}
          cy={core.y}
          r="3.5"
          fill={i % 2 ? C.violet : C.cyan}
          {...anim('ba-move', i * 0.3, { '--tx': `${(n.x - core.x) / 2}px`, '--ty': `${(n.y - core.y) / 2}px`, '--tx2': `${n.x - core.x}px`, '--ty2': `${n.y - core.y}px`, '--d': '2.6s' })}
        />
      ))}
      {nodes.map((n, i) => (
        <g key={`n${i}`}>
          <rect x={n.x - 12} y={n.y - 8} width="24" height="16" rx="4" fill="#0f172a" stroke={i % 2 ? C.violet : C.cyan} strokeOpacity="0.7" />
          <circle cx={n.x + 6} cy={n.y} r="2" fill={C.mint} {...anim('ba-blink', i * 0.2)} />
        </g>
      ))}
      <circle cx={core.x} cy={core.y} r="16" fill={C.cyan} fillOpacity="0.2" {...anim('ba-ping', 0, { '--d': '2.6s' }, `${core.x}px ${core.y}px`)} />
      <rect x={core.x - 16} y={core.y - 11} width="32" height="22" rx="5" fill="#0e7490" stroke={C.cyan} />
      {[0, 1, 2].map((i) => (
        <circle key={i} cx={core.x - 7 + i * 7} cy={core.y} r="2" fill="#fff" />
      ))}
    </Svg>
  )
}

const SOLUTIONS = {
  website: SolWebsite,
  management: SolManagement,
  ecommerce: SolShop,
  automation: SolAutomation,
  hosting: SolHosting,
  network: SolNetwork,
} satisfies Record<string, () => JSX.Element>

export type SolutionKind = keyof typeof SOLUTIONS

export function SolutionArt({ kind }: { kind: SolutionKind }) {
  const Art = SOLUTIONS[kind]
  return <Art />
}

// ---------------------------------------------------------------------------
// Process
// ---------------------------------------------------------------------------

/** Discover — a magnifier searches scattered issues and finds the real one. */
function ProcDiscover() {
  const dots = [
    [30, 30], [62, 70], [96, 24], [128, 84], [150, 44], [190, 76], [214, 28], [250, 62], [282, 34], [296, 86], [44, 92], [176, 16],
  ]
  return (
    <Svg>
      {dots.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="4" fill="#94a3b8" fillOpacity="0.35" />
      ))}
      <circle cx="250" cy="62" r="12" fill={C.amber} fillOpacity="0.3" {...anim('ba-ping', 2.2, { '--d': '4.4s' }, '250px 62px')} />
      <circle cx="250" cy="62" r="6" fill={C.amber} {...anim('ba-pop', 2, { '--d': '4.4s' })} />
      <g {...anim('ba-move', 0, { '--tx': '90px', '--ty': '-10px', '--tx2': '170px', '--ty2': '22px', '--d': '4.4s' })}>
        <circle cx="80" cy="40" r="20" fill={C.cyan} fillOpacity="0.1" stroke={C.cyan} strokeWidth="4" />
        <path d="M94 54l14 14" stroke={C.cyan} strokeWidth="6" strokeLinecap="round" />
      </g>
    </Svg>
  )
}

/** Scope — features, timeline and budget ticked off one by one. */
function ProcScope() {
  const items = ['Features', 'Timeline', 'Budget', 'Your approval']
  return (
    <Svg>
      <rect x="10" y="4" width="196" height="102" rx="8" fill="#000" fillOpacity="0.25" stroke="#fff" strokeOpacity="0.12" />
      {items.map((t, i) => (
        <g key={t}>
          <rect x="22" y={14 + i * 23} width="16" height="16" rx="4" stroke="#fff" strokeOpacity="0.35" strokeWidth="1.5" />
          <path d={`M26 ${22 + i * 23}l3.5 3.5 6-7`} stroke={C.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" pathLength={100} {...anim('ba-draw', 0.3 + i * 0.6, { '--d': '6s' })} />
          <text x="48" y={26 + i * 23} fontSize="10.5" fill="#e2e8f0" fillOpacity="0.85">
            {t}
          </text>
        </g>
      ))}
      <g {...anim('ba-pop', 2.8, { '--d': '6s' })}>
        <rect x="222" y="22" width="90" height="66" rx="10" fill={C.mint} fillOpacity="0.12" stroke={C.mint} strokeOpacity="0.6" />
        <circle cx="267" cy="46" r="11" fill={C.mint} />
        <path d="M261 46l4 4 8-9" stroke="#04261a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <text x="267" y="76" textAnchor="middle" fontSize="10" fontWeight="700" fill={C.mint}>
          Agreed
        </text>
      </g>
    </Svg>
  )
}

/** Build & track — milestones fill in while the client portal updates. */
function ProcBuild() {
  const xs = [24, 74, 124, 174]
  return (
    <Svg>
      <rect x="20" y="40" width="160" height="4" rx="2" fill="#fff" fillOpacity="0.12" />
      <rect x="20" y="40" width="156" height="4" rx="2" fill="url(#pb-grad)" {...anim('ba-grow', 0, { '--d': '6s' }, '20px 42px')} />
      {xs.map((x, i) => (
        <g key={x}>
          <circle cx={x} cy="42" r="9" fill="#0f172a" stroke="#fff" strokeOpacity="0.3" strokeWidth="2" />
          <circle cx={x} cy="42" r="6" fill={i % 2 ? C.violet : C.cyan} {...anim('ba-pop', 0.3 + i * 1.1, { '--d': '6s' })} />
          <text x={x} y="66" textAnchor="middle" fontSize="8.5" fill="#94a3b8">
            M{i + 1}
          </text>
        </g>
      ))}
      <rect x="204" y="8" width="108" height="94" rx="8" fill="#000" fillOpacity="0.3" stroke="#fff" strokeOpacity="0.12" />
      <text x="214" y="24" fontSize="8.5" fill="#94a3b8">
        Client portal
      </text>
      {[24, 32, 40, 46].map((h, i) => (
        <rect
          key={i}
          x={218 + i * 22}
          y={90 - h}
          width="14"
          height={h}
          rx="3"
          fill={i % 2 ? C.violet : C.cyan}
          fillOpacity="0.75"
          {...anim('ba-growy', 0.3 + i * 1.1, { '--d': '6s' }, `${225 + i * 22}px 90px`)}
        />
      ))}
      <defs>
        <linearGradient id="pb-grad" x1="0" x2="1">
          <stop offset="0" stopColor={C.cyan} />
          <stop offset="1" stopColor={C.violet} />
        </linearGradient>
      </defs>
    </Svg>
  )
}

/** Launch & support — the rocket lifts off, then a steady support heartbeat. */
function ProcLaunch() {
  return (
    <Svg>
      <path d="M70 104V70" stroke={C.amber} strokeOpacity="0.5" strokeWidth="3" strokeDasharray="4 6" {...anim('ba-flow', 0, { '--d': '0.6s', '--dash-end': -10 })} />
      <g {...anim('ba-float', 0, { '--d': '3s' })}>
        <path d="M70 6c14 10 18 30 14 50H56C52 36 56 16 70 6z" fill="#e2e8f0" />
        <circle cx="70" cy="30" r="6" fill={C.cyan} stroke="#0f172a" strokeWidth="2" />
        <path d="M56 46l-10 14 12-2zM84 46l10 14-12-2z" fill={C.violet} />
        <path d="M62 58h16l-8 16z" fill={C.amber} {...anim('ba-twinkle', 0, { '--d': '0.35s' }, '70px 58px')} />
      </g>
      <text x="130" y="30" fontSize="10" fontWeight="700" fill={C.amber}>
        Live
      </text>
      <text x="130" y="88" fontSize="10" fontWeight="700" fill={C.mint}>
        Support
      </text>
      <path
        d="M130 66 H180 L188 50 L198 82 L208 40 L218 74 L226 66 H310"
        stroke={C.mint}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={100}
        {...anim('ba-draw', 0.4, { '--d': '3.2s' })}
      />
      <circle cx="300" cy="66" r="6" fill={C.mint} fillOpacity="0.3" {...anim('ba-ping', 1.4, { '--d': '3.2s' }, '300px 66px')} />
    </Svg>
  )
}

const PROCESS = { discover: ProcDiscover, scope: ProcScope, build: ProcBuild, launch: ProcLaunch } satisfies Record<
  string,
  () => JSX.Element
>

export type ProcessKind = keyof typeof PROCESS

export function ProcessArt({ kind }: { kind: ProcessKind }) {
  const Art = PROCESS[kind]
  return <Art />
}

// ---------------------------------------------------------------------------
// Services
// ---------------------------------------------------------------------------

const SVB = '0 0 320 120'

/** Web design — a page assembles itself and the cursor clicks the button. */
function SrvWeb() {
  const blocks = [
    { x: 20, y: 24, w: 280, h: 10, c: '#fff', o: 0.15 },
    { x: 20, y: 40, w: 150, h: 10, c: C.cyan, o: 0.7 },
    { x: 20, y: 55, w: 110, h: 6, c: '#fff', o: 0.35 },
    { x: 20, y: 67, w: 60, h: 14, c: C.violet, o: 0.85 },
    { x: 196, y: 40, w: 104, h: 41, c: '#fff', o: 0.1 },
    { x: 20, y: 90, w: 86, h: 22, c: '#fff', o: 0.08 },
    { x: 117, y: 90, w: 86, h: 22, c: '#fff', o: 0.08 },
    { x: 214, y: 90, w: 86, h: 22, c: '#fff', o: 0.08 },
  ]
  return (
    <Svg vb={SVB}>
      <rect x="10" y="6" width="300" height="112" rx="8" fill="#000" fillOpacity="0.25" stroke="#fff" strokeOpacity="0.12" />
      {[0, 1, 2].map((i) => (
        <circle key={i} cx={20 + i * 8} cy="14" r="2.2" fill="#fff" fillOpacity="0.35" />
      ))}
      {blocks.map((b, i) => (
        <rect key={i} x={b.x} y={b.y} width={b.w} height={b.h} rx="3" fill={b.c} fillOpacity={b.o} {...anim('ba-pop', i * 0.25, { '--d': '6s' })} />
      ))}
      <circle cx="50" cy="74" r="10" fill="#fff" fillOpacity="0.4" {...anim('ba-ping', 3.4, { '--d': '6s' }, '50px 74px')} />
      <g transform="translate(250 100)">
        <path
          d="M0 0l0 16 4.5-4 3 7 3-1.5-3-7 6 0z"
          fill="#fff"
          stroke="#0f172a"
          strokeWidth="1"
          {...anim('ba-move', 2, { '--tx': '-198px', '--ty': '-26px', '--tx2': '-198px', '--ty2': '-26px', '--d': '6s' })}
        />
      </g>
    </Svg>
  )
}

/** Software — code types itself while the gears turn. */
function SrvSoftware() {
  const lines = [
    { x: 0, w: 90, c: C.violet },
    { x: 12, w: 120, c: '#e2e8f0' },
    { x: 24, w: 70, c: C.cyan },
    { x: 24, w: 104, c: '#e2e8f0' },
    { x: 12, w: 50, c: C.mint },
    { x: 0, w: 20, c: C.violet },
  ]
  return (
    <Svg vb={SVB}>
      <rect x="10" y="8" width="200" height="104" rx="8" fill="#020617" fillOpacity="0.7" stroke="#fff" strokeOpacity="0.12" />
      {lines.map((l, i) => (
        <g key={i}>
          <text x="18" y={31 + i * 14} fontSize="8" fill="#475569" fontFamily="ui-monospace, monospace">
            {i + 1}
          </text>
          <rect x={32 + l.x} y={25 + i * 14} width={l.w} height="6" rx="3" fill={l.c} fillOpacity="0.8" {...anim('ba-type', i * 0.5, { '--d': '6s' })} />
        </g>
      ))}
      <g {...anim('ba-spin', 0, { '--d': '7s' }, '256px 52px')}>
        <circle cx="256" cy="52" r="24" stroke={C.violet} strokeWidth="9" strokeDasharray="8 6.5" />
        <circle cx="256" cy="52" r="9" fill={C.violet} fillOpacity="0.8" />
      </g>
      <g {...anim('ba-spin-r', 0, { '--d': '4.5s' }, '290px 92px')}>
        <circle cx="290" cy="92" r="14" stroke={C.cyan} strokeWidth="7" strokeDasharray="5.5 5" />
        <circle cx="290" cy="92" r="5" fill={C.cyan} />
      </g>
    </Svg>
  )
}

/** Project development — a task card moves across the board to done. */
function SrvProject() {
  const cols = ['To do', 'Doing', 'Done']
  return (
    <Svg vb={SVB}>
      {cols.map((c, i) => (
        <g key={c}>
          <rect x={12 + i * 100} y="8" width="94" height="94" rx="8" fill="#fff" fillOpacity="0.05" stroke="#fff" strokeOpacity="0.1" />
          <text x={22 + i * 100} y="24" fontSize="9" fontWeight="700" fill={[C.cyan, C.amber, C.mint][i]}>
            {c}
          </text>
          {[0, 1].map((j) => (
            <rect key={j} x={20 + i * 100} y={60 + j * 18} width="78" height="13" rx="3" fill="#fff" fillOpacity="0.1" />
          ))}
        </g>
      ))}
      <g {...anim('ba-move', 0, { '--tx': '100px', '--ty': '0px', '--tx2': '200px', '--ty2': '0px', '--d': '6s' })}>
        <rect x="20" y="32" width="78" height="22" rx="4" fill={C.cyan} fillOpacity="0.85" />
        <rect x="27" y="39" width="44" height="4" rx="2" fill="#052730" fillOpacity="0.7" />
        <rect x="27" y="46" width="28" height="3" rx="1.5" fill="#052730" fillOpacity="0.5" />
      </g>
      <rect x="12" y="110" width="294" height="4" rx="2" fill="#fff" fillOpacity="0.1" />
      <rect x="12" y="110" width="294" height="4" rx="2" fill={C.mint} {...anim('ba-grow', 0, { '--d': '6s' }, '12px 112px')} />
    </Svg>
  )
}

/** IT consultancy — question in, idea glows, results climb. */
function SrvConsult() {
  return (
    <Svg vb={SVB}>
      <g {...anim('ba-pop', 0, { '--d': '6s' })}>
        <rect x="14" y="12" width="96" height="30" rx="10" fill="#fff" fillOpacity="0.1" />
        <text x="62" y="32" textAnchor="middle" fontSize="11" fontWeight="700" fill="#e2e8f0">
          How do we grow?
        </text>
      </g>
      <g {...anim('ba-pop', 0.8, { '--d': '6s' })}>
        <rect x="14" y="52" width="96" height="30" rx="10" fill={C.cyan} fillOpacity="0.25" />
        <text x="62" y="72" textAnchor="middle" fontSize="11" fontWeight="700" fill={C.cyan}>
          Here is the plan
        </text>
      </g>
      <g transform="translate(150 20)">
        {[0, 45, 90, 135, 180, 225, 270, 315].map((a, i) => (
          <line
            key={a}
            x1="20"
            y1="-6"
            x2="20"
            y2="-14"
            stroke={C.amber}
            strokeWidth="2.5"
            strokeLinecap="round"
            transform={`rotate(${a} 20 22)`}
            {...anim('ba-blink', i * 0.12, { '--d': '0.9s' })}
          />
        ))}
        <circle cx="20" cy="22" r="14" fill={C.amber} fillOpacity="0.85" />
        <rect x="13" y="36" width="14" height="10" rx="2" fill="#94a3b8" />
      </g>
      <path d="M200 104 H310 M200 104 V16" stroke="#fff" strokeOpacity="0.2" />
      <path
        d="M204 96 L228 84 L248 88 L268 64 L288 52 L306 28"
        stroke={C.mint}
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={100}
        {...anim('ba-draw', 1.2, { '--d': '6s' })}
      />
      <path d="M298 26 L307 27 L304 36" stroke={C.mint} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" {...anim('ba-pop', 3.2, { '--d': '6s' })} />
    </Svg>
  )
}

/** Hosting & domains — a satellite circles the globe, the domain types in. */
function SrvHosting() {
  return (
    <Svg vb={SVB}>
      <circle cx="70" cy="60" r="36" fill={C.cyan} fillOpacity="0.12" stroke={C.cyan} strokeWidth="2" />
      <ellipse cx="70" cy="60" rx="14" ry="36" stroke={C.cyan} strokeOpacity="0.6" />
      <ellipse cx="70" cy="60" rx="30" ry="36" stroke={C.cyan} strokeOpacity="0.3" />
      <path d="M34 60h72M40 42h60M40 78h60" stroke={C.cyan} strokeOpacity="0.4" />
      <ellipse cx="70" cy="60" rx="54" ry="18" stroke={C.violet} strokeOpacity="0.4" strokeDasharray="3 5" transform="rotate(-20 70 60)" />
      <g {...anim('ba-spin', 0, { '--d': '5s' }, '70px 60px')}>
        <circle cx="124" cy="60" r="5" fill={C.violet} />
        <circle cx="124" cy="60" r="10" fill={C.violet} fillOpacity="0.25" />
      </g>
      <rect x="146" y="40" width="164" height="40" rx="20" fill="#fff" fillOpacity="0.08" stroke="#fff" strokeOpacity="0.2" />
      <path d="M162 58v-4a5 5 0 0 1 10 0v4" stroke={C.mint} strokeWidth="2" />
      <rect x="159" y="57" width="16" height="12" rx="3" fill={C.mint} />
      <text x="184" y="65" fontSize="12.5" fontWeight="600" fill="#e2e8f0" {...anim('ba-type', 0.4, { '--d': '6s' })}>
        yourbusiness.rw
      </text>
      <circle cx="294" cy="60" r="5" fill={C.mint} {...anim('ba-blink', 0)} />
    </Svg>
  )
}

/** Installation & IT solutions — Wi-Fi waves reach each device and connect it. */
function SrvInstall() {
  const devices = [
    { x: 30, y: 26, w: 46, h: 30 },
    { x: 244, y: 22, w: 46, h: 30 },
    { x: 34, y: 84, w: 22, h: 30 },
    { x: 264, y: 82, w: 22, h: 30 },
  ]
  return (
    <Svg vb={SVB}>
      {devices.map((d, i) => (
        <g key={i}>
          <path
            d={`M160 84 L${d.x + d.w / 2} ${d.y + d.h / 2}`}
            stroke={C.cyan}
            strokeOpacity="0.7"
            strokeWidth="1.5"
            strokeDasharray="4 4"
            {...anim('ba-flow', i * 0.2, { '--d': '1s', '--dash-end': -8 })}
          />
          <rect x={d.x} y={d.y} width={d.w} height={d.h} rx="4" fill="#0f172a" stroke="#fff" strokeOpacity="0.4" />
          <circle cx={d.x + d.w - 5} cy={d.y + 5} r="3" fill={C.mint} {...anim('ba-pop', 0.6 + i * 0.5, { '--d': '5s' })} />
        </g>
      ))}
      {[18, 32, 46].map((r, i) => (
        <path
          key={r}
          d={`M${160 - r} ${78 - r * 0.2} A ${r} ${r} 0 0 1 ${160 + r} ${78 - r * 0.2}`}
          stroke={C.cyan}
          strokeWidth="3"
          strokeLinecap="round"
          {...anim('ba-blink', i * 0.3, { '--d': '0.9s' })}
        />
      ))}
      <rect x="136" y="78" width="48" height="20" rx="5" fill="#0e7490" stroke={C.cyan} />
      <path d="M144 78v-10M176 78v-10" stroke={C.cyan} strokeWidth="2" strokeLinecap="round" />
      {[0, 1, 2].map((i) => (
        <circle key={i} cx={150 + i * 10} cy="88" r="2.2" fill="#fff" {...anim('ba-blink', i * 0.2, { '--d': '0.6s' })} />
      ))}
    </Svg>
  )
}

/** Research & technical support — a magnifier reads the report, findings chart. */
function SrvResearch() {
  return (
    <Svg vb={SVB}>
      <rect x="20" y="10" width="120" height="100" rx="6" fill="#fff" fillOpacity="0.92" />
      {Array.from({ length: 8 }).map((_, i) => (
        <rect key={i} x="32" y={22 + i * 10} width={i % 3 === 2 ? 60 : 96} height="4" rx="2" fill="#334155" fillOpacity="0.5" />
      ))}
      <g {...anim('ba-move', 0, { '--tx': '50px', '--ty': '26px', '--tx2': '8px', '--ty2': '52px', '--d': '6s' })}>
        <circle cx="62" cy="34" r="16" fill={C.cyan} fillOpacity="0.15" stroke="#0e7490" strokeWidth="4" />
        <path d="M74 46l12 12" stroke="#0e7490" strokeWidth="6" strokeLinecap="round" />
      </g>
      <path d="M170 106 H310" stroke="#fff" strokeOpacity="0.25" />
      {[44, 64, 36, 80, 58].map((h, i) => (
        <rect
          key={i}
          x={178 + i * 26}
          y={106 - h}
          width="16"
          height={h}
          rx="3"
          fill={i === 3 ? C.violet : C.cyan}
          fillOpacity="0.8"
          {...anim('ba-growy', i * 0.3, { '--d': '6s' }, `${186 + i * 26}px 106px`)}
        />
      ))}
    </Svg>
  )
}

/** Electronics & technology — current pulses along circuit traces to the chip. */
function SrvElectronics() {
  const traces = [
    'M20 30 H90 V48 H128',
    'M20 90 H70 V72 H128',
    'M300 24 H240 V48 H192',
    'M300 96 H250 V72 H192',
    'M160 8 V36',
    'M160 112 V84',
  ]
  return (
    <Svg vb={SVB}>
      {traces.map((d, i) => (
        <g key={i}>
          <path d={d} stroke="#34d399" strokeOpacity="0.25" strokeWidth="2.5" />
          <path d={d} stroke={i % 2 ? C.cyan : C.mint} strokeWidth="2.5" strokeLinecap="round" strokeDasharray="6 30" {...anim('ba-flow', i * 0.25, { '--d': '1.2s', '--dash-end': -36 })} />
        </g>
      ))}
      {[[20, 30], [20, 90], [300, 24], [300, 96]].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="5" fill="#0f172a" stroke={C.mint} strokeWidth="2" />
      ))}
      <rect x="128" y="36" width="64" height="48" rx="6" fill="#111827" stroke={C.mint} strokeWidth="2" />
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <rect x={136 + i * 14} y="30" width="5" height="6" fill="#94a3b8" />
          <rect x={136 + i * 14} y="84" width="5" height="6" fill="#94a3b8" />
        </g>
      ))}
      <text x="160" y="64" textAnchor="middle" fontSize="11" fontWeight="800" fill={C.mint} fontFamily="ui-monospace, monospace">
        CPU
      </text>
      <circle cx="182" cy="44" r="3" fill={C.amber} {...anim('ba-blink', 0, { '--d': '0.7s' })} />
    </Svg>
  )
}

function Sparkle({ x, y, s, delay, color }: { x: number; y: number; s: number; delay: number; color: string }) {
  return (
    <path
      d={`M${x} ${y - s} Q${x} ${y} ${x + s} ${y} Q${x} ${y} ${x} ${y + s} Q${x} ${y} ${x - s} ${y} Q${x} ${y} ${x} ${y - s}Z`}
      fill={color}
      {...anim('ba-twinkle', delay, { '--d': '2.2s' }, `${x}px ${y}px`)}
    />
  )
}

/** Beauty gadgets & tools — a compact mirror catches the light and sparkles. */
function SrvBeauty() {
  return (
    <Svg vb={SVB}>
      <defs>
        <clipPath id="sb-mirror">
          <circle cx="130" cy="58" r="40" />
        </clipPath>
        <linearGradient id="sb-rose" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stopColor="#f9a8d4" />
          <stop offset="1" stopColor="#b76e79" />
        </linearGradient>
      </defs>
      <circle cx="130" cy="58" r="48" fill="url(#sb-rose)" />
      <circle cx="130" cy="58" r="40" fill="#e0f2fe" fillOpacity="0.9" />
      <g clipPath="url(#sb-mirror)">
        <g transform="rotate(20 130 58)">
          <rect x="40" y="-20" width="22" height="160" fill="#fff" fillOpacity="0.7" {...anim('ba-move', 0, { '--tx': '60px', '--ty': '0px', '--tx2': '120px', '--ty2': '0px', '--d': '3.6s' })} />
        </g>
      </g>
      <rect x="196" y="40" width="90" height="16" rx="8" fill="url(#sb-rose)" transform="rotate(-25 241 48)" />
      <rect x="270" y="20" width="22" height="22" rx="4" fill="#fbcfe8" transform="rotate(-25 241 48)" />
      <Sparkle x={70} y={22} s={9} delay={0} color="#fff" />
      <Sparkle x={196} y={96} s={8} delay={0.7} color="#fbcfe8" />
      <Sparkle x={178} y={20} s={6} delay={1.3} color="#fff" />
      <Sparkle x={90} y={104} s={6} delay={1.8} color="#f9a8d4" />
      <Sparkle x={292} y={92} s={7} delay={0.4} color="#fff" />
    </Svg>
  )
}

/** Fallback for a service with no specific art — orbiting signals. */
function SrvGeneric() {
  return (
    <Svg vb={SVB}>
      {[22, 38, 54].map((r, i) => (
        <circle key={r} cx="160" cy="60" r={r} stroke={i === 1 ? C.violet : C.cyan} strokeOpacity="0.4" />
      ))}
      {[22, 38, 54].map((r, i) => (
        <g key={`o${r}`} {...anim(i % 2 ? 'ba-spin-r' : 'ba-spin', 0, { '--d': `${4 + i * 2}s` }, '160px 60px')}>
          <circle cx={160 + r} cy="60" r="4.5" fill={i === 1 ? C.violet : C.cyan} />
        </g>
      ))}
      <circle cx="160" cy="60" r="8" fill="#fff" {...anim('ba-twinkle', 0, { '--d': '2.4s' }, '160px 60px')} />
    </Svg>
  )
}

const SERVICE_RULES: [RegExp, () => JSX.Element][] = [
  [/web|site|design/i, SrvWeb],
  [/software|app|system/i, SrvSoftware],
  [/project/i, SrvProject],
  [/consult|advice|strategy/i, SrvConsult],
  [/host|domain|cloud/i, SrvHosting],
  [/install|network|infra|it solution/i, SrvInstall],
  [/research|support|training/i, SrvResearch],
  [/electronic|technology|hardware/i, SrvElectronics],
  [/beauty|gadget|cosmetic/i, SrvBeauty],
]

export function ServiceArt({ name }: { name: string }) {
  const Art = SERVICE_RULES.find(([re]) => re.test(name))?.[1] ?? SrvGeneric
  return <Art />
}
