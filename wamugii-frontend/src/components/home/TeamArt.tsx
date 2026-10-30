import type { CSSProperties, JSX, ReactNode } from 'react'

/**
 * Animated illustrations for the "Our principles", "Why WAMUGII" and
 * "From idea to working technology" sections. Each one is drawn for its own
 * message and none repeats a motif used elsewhere on the homepage. Shares the
 * `.ba-*` animation vocabulary (index.css) and needs an <AnimInView> parent.
 */

type Vars = Record<string, string | number>

function anim(cls: string, delay = 0, vars: Vars = {}, origin?: string): { className: string; style: CSSProperties } {
  const style: Record<string, string | number> = { animationDelay: `${delay}s`, ...vars }
  if (origin) style.transformOrigin = origin
  return { className: cls, style: style as CSSProperties }
}

const C = { cyan: '#22d3ee', violet: '#a78bfa', mint: '#34d399', pink: '#f472b6', amber: '#fbbf24', red: '#f87171', sky: '#38bdf8' }

function Svg({ children, vb = '0 0 320 120' }: { children: ReactNode; vb?: string }) {
  return (
    <svg viewBox={vb} preserveAspectRatio="xMidYMid meet" className="h-full w-full" fill="none">
      {children}
    </svg>
  )
}

// ---------------------------------------------------------------------------
// Our principles
// ---------------------------------------------------------------------------

/** Built around your needs — requirement pieces slot into the blueprint. */
function Blueprint() {
  const slots = [
    { x: 150, y: 18, w: 70, h: 34, c: C.cyan },
    { x: 228, y: 18, w: 70, h: 34, c: C.violet },
    { x: 150, y: 60, w: 148, h: 40, c: C.mint },
  ]
  return (
    <Svg>
      <defs>
        <pattern id="bp-grid" width="12" height="12" patternUnits="userSpaceOnUse">
          <path d="M12 0H0V12" stroke="#38bdf8" strokeOpacity="0.15" />
        </pattern>
      </defs>
      <rect x="140" y="8" width="168" height="104" rx="6" fill="#0c4a6e" fillOpacity="0.35" />
      <rect x="140" y="8" width="168" height="104" rx="6" fill="url(#bp-grid)" stroke={C.sky} strokeOpacity="0.5" />
      {slots.map((s, i) => (
        <rect key={`s${i}`} x={s.x} y={s.y} width={s.w} height={s.h} rx="4" stroke={s.c} strokeOpacity="0.6" strokeDasharray="4 3" />
      ))}
      {/* the "requirements" start on the left as notes and fly into place */}
      {slots.map((s, i) => {
        const fromX = 14
        const fromY = 10 + i * 36
        return (
          <g key={i} {...anim('ba-move', i * 0.6, { '--tx': `${(s.x - fromX) * 0.55}px`, '--ty': `${(s.y - fromY) * 0.55}px`, '--tx2': `${s.x - fromX}px`, '--ty2': `${s.y - fromY}px`, '--d': '6s' })}>
            <rect x={fromX} y={fromY} width={s.w} height={s.h} rx="4" fill={s.c} fillOpacity="0.85" />
            <rect x={fromX + 6} y={fromY + 7} width={s.w * 0.55} height="4" rx="2" fill="#0f172a" fillOpacity="0.55" />
            <rect x={fromX + 6} y={fromY + 15} width={s.w * 0.35} height="3" rx="1.5" fill="#0f172a" fillOpacity="0.4" />
          </g>
        )
      })}
      <text x="300" y="108" textAnchor="end" fontSize="8" fill={C.sky} fillOpacity="0.8" fontFamily="ui-monospace, monospace">
        YOUR PROCESS
      </text>
    </Svg>
  )
}

/** Secure by design — threats bounce off a turning shield ring; the lock holds. */
function SecureCore() {
  const threats = [
    { x: 20, y: 20 }, { x: 300, y: 24 }, { x: 18, y: 100 }, { x: 302, y: 96 }, { x: 160, y: 4 },
  ]
  const cx = 160
  const cy = 62
  return (
    <Svg>
      {threats.map((t, i) => {
        const dx = cx - t.x
        const dy = cy - t.y
        const len = Math.hypot(dx, dy)
        const stop = (len - 50) / len
        return (
          <circle
            key={i}
            cx={t.x}
            cy={t.y}
            r="4"
            fill={C.red}
            {...anim('ba-move', i * 0.55, { '--tx': `${dx * stop * 0.6}px`, '--ty': `${dy * stop * 0.6}px`, '--tx2': `${dx * stop}px`, '--ty2': `${dy * stop}px`, '--d': '2.8s' })}
          />
        )
      })}
      <polygon
        points={Array.from({ length: 6 }, (_, k) => {
          const a = (Math.PI / 3) * k - Math.PI / 2
          return `${cx + 48 * Math.cos(a)},${cy + 48 * Math.sin(a)}`
        }).join(' ')}
        stroke={C.cyan}
        strokeWidth="2.5"
        strokeDasharray="10 6"
        fill={C.cyan}
        fillOpacity="0.06"
        {...anim('ba-spin', 0, { '--d': '14s' }, `${cx}px ${cy}px`)}
      />
      <circle cx={cx} cy={cy} r="34" stroke={C.violet} strokeOpacity="0.5" strokeDasharray="2 5" {...anim('ba-spin-r', 0, { '--d': '9s' }, `${cx}px ${cy}px`)} />
      <circle cx={cx} cy={cy} r="24" fill={C.cyan} fillOpacity="0.15" {...anim('ba-ping', 0, { '--d': '2.8s' }, `${cx}px ${cy}px`)} />
      <path d={`M${cx - 9} ${cy - 2}v-6a9 9 0 0 1 18 0v6`} stroke="#e2e8f0" strokeWidth="3.5" strokeLinecap="round" />
      <rect x={cx - 14} y={cy - 3} width="28" height="22" rx="5" fill="#e2e8f0" />
      <circle cx={cx} cy={cy + 6} r="3" fill="#0f172a" />
      <rect x={cx - 1.2} y={cy + 6} width="2.4" height="7" rx="1" fill="#0f172a" />
    </Svg>
  )
}

/** Ready to scale — users arrive, servers multiply, the gauge stays in green. */
function ScaleGauge() {
  const gx = 80
  const gy = 92
  return (
    <Svg>
      <path d={`M${gx - 56} ${gy} A56 56 0 0 1 ${gx + 56} ${gy}`} stroke="#fff" strokeOpacity="0.12" strokeWidth="12" strokeLinecap="round" />
      <path d={`M${gx - 56} ${gy} A56 56 0 0 1 ${gx + 20} ${gy - 52}`} stroke={C.mint} strokeWidth="12" strokeLinecap="round" />
      <path d={`M${gx + 20} ${gy - 52} A56 56 0 0 1 ${gx + 56} ${gy}`} stroke={C.amber} strokeOpacity="0.35" strokeWidth="12" strokeLinecap="round" />
      <g {...anim('ba-swing', 0, { '--r1': '-75deg', '--r2': '25deg', '--d': '4s' }, `${gx}px ${gy}px`)}>
        <path d={`M${gx} ${gy} L${gx} ${gy - 46}`} stroke="#fff" strokeWidth="3.5" strokeLinecap="round" />
      </g>
      <circle cx={gx} cy={gy} r="7" fill="#fff" />
      <text x={gx} y="116" textAnchor="middle" fontSize="8.5" fill="#94a3b8">
        load
      </text>
      {/* users */}
      {Array.from({ length: 8 }).map((_, i) => (
        <g key={i} {...anim('ba-pop', i * 0.25, { '--d': '6s' })}>
          <circle cx={170 + (i % 4) * 16} cy={i < 4 ? 16 : 36} r="4" fill={C.violet} />
          <path d={`M${163 + (i % 4) * 16} ${i < 4 ? 28 : 48}a7 6 0 0 1 14 0z`} fill={C.violet} />
        </g>
      ))}
      {/* servers: 1, then 2, then 4 */}
      {Array.from({ length: 4 }).map((_, i) => (
        <g key={`v${i}`} {...anim('ba-pop', [0, 1.5, 3, 3.2][i]!, { '--d': '6s' })}>
          <rect x={168 + (i % 2) * 66} y={60 + Math.floor(i / 2) * 28} width="58" height="22" rx="4" fill="#fff" fillOpacity="0.08" stroke={C.mint} strokeOpacity="0.6" />
          <circle cx={216 + (i % 2) * 66} cy={71 + Math.floor(i / 2) * 28} r="3" fill={C.mint} {...anim('ba-blink', i * 0.2, { '--d': '0.8s' })} />
          <rect x={176 + (i % 2) * 66} y={69 + Math.floor(i / 2) * 28} width="26" height="4" rx="2" fill="#fff" fillOpacity="0.2" />
        </g>
      ))}
    </Svg>
  )
}

/** Supported beyond launch — a version timeline keeps moving, the wrench keeps working. */
function SupportTimeline() {
  const versions = ['v1.0', 'v1.1', 'v1.2', 'v1.3', 'v2.0']
  return (
    <Svg>
      <path d="M14 84 H306" stroke="#fff" strokeOpacity="0.15" strokeWidth="2" />
      {versions.map((v, i) => (
        <g key={v} {...anim('ba-pop', i * 0.7, { '--d': '7s' })}>
          <circle cx={30 + i * 64} cy="84" r="7" fill="#0f172a" stroke={i === 4 ? C.amber : C.cyan} strokeWidth="2.5" />
          <circle cx={30 + i * 64} cy="84" r="3" fill={i === 4 ? C.amber : C.cyan} />
          <rect x={14 + i * 64} y="96" width="32" height="15" rx="7.5" fill={i === 4 ? C.amber : C.cyan} fillOpacity="0.18" />
          <text x={30 + i * 64} y="107" textAnchor="middle" fontSize="8.5" fontWeight="700" fill={i === 4 ? C.amber : '#a5f3fc'}>
            {v}
          </text>
        </g>
      ))}
      <rect x="14" y="83" width="292" height="2" fill={C.cyan} {...anim('ba-grow', 0, { '--d': '7s' }, '14px 84px')} />
      {/* wrench working on a cog */}
      <g {...anim('ba-spin', 0, { '--d': '6s' }, '120px 38px')}>
        <circle cx="120" cy="38" r="20" stroke={C.violet} strokeWidth="8" strokeDasharray="7 5.5" />
        <circle cx="120" cy="38" r="7" fill={C.violet} />
      </g>
      <g {...anim('ba-swing', 0, { '--r1': '-25deg', '--r2': '15deg', '--d': '1.4s' }, '172px 52px')}>
        <path d="M172 52 L140 30" stroke="#e2e8f0" strokeWidth="7" strokeLinecap="round" />
        <path d="M132 22a10 10 0 1 0 14 14l-5-5 2-6-6 2z" fill="#e2e8f0" />
      </g>
      <g {...anim('ba-pop', 2.6, { '--d': '7s' })}>
        <rect x="204" y="16" width="102" height="34" rx="12" fill={C.mint} fillOpacity="0.18" stroke={C.mint} strokeOpacity="0.6" />
        <path d="M218 33l4 4 8-9" stroke={C.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        <text x="238" y="37" fontSize="11" fontWeight="700" fill={C.mint}>
          Fixed &amp; updated
        </text>
      </g>
    </Svg>
  )
}

const PRINCIPLES = { needs: Blueprint, secure: SecureCore, scale: ScaleGauge, support: SupportTimeline } satisfies Record<
  string,
  () => JSX.Element
>
export type PrincipleKind = keyof typeof PRINCIPLES
export function PrincipleArt({ kind }: { kind: PrincipleKind }) {
  const Art = PRINCIPLES[kind]
  return <Art />
}

// ---------------------------------------------------------------------------
// Why WAMUGII
// ---------------------------------------------------------------------------

/** Lead card — your live client portal: activity arrives, files drop in. */
function LivePortal() {
  const feed = [
    { c: C.cyan, w: 92, t: 'Design approved' },
    { c: C.violet, w: 110, t: 'Milestone 2 started' },
    { c: C.mint, w: 84, t: 'New file shared' },
    { c: C.amber, w: 100, t: 'Progress 68%' },
  ]
  return (
    <Svg vb="0 0 320 180">
      <rect x="6" y="6" width="308" height="168" rx="10" fill="#020617" fillOpacity="0.55" stroke="#fff" strokeOpacity="0.12" />
      <rect x="6" y="6" width="70" height="168" rx="10" fill="#fff" fillOpacity="0.04" />
      {[0, 1, 2, 3].map((i) => (
        <rect key={i} x="16" y={42 + i * 20} width={i === 0 ? 50 : 40} height="8" rx="4" fill={i === 0 ? C.cyan : '#fff'} fillOpacity={i === 0 ? 0.6 : 0.15} />
      ))}
      <circle cx="26" cy="22" r="8" fill="url(#lp-av)" />
      <text x="90" y="26" fontSize="10" fontWeight="700" fill="#e2e8f0">
        Your project
      </text>
      <circle cx="292" cy="22" r="4" fill={C.red} {...anim('ba-blink', 0, { '--d': '0.7s' })} />
      <text x="284" y="25.5" fontSize="8" fontWeight="700" textAnchor="end" fill={C.red}>
        LIVE
      </text>
      {feed.map((f, i) => (
        <g key={f.t} {...anim('ba-pop', 0.3 + i * 0.8, { '--d': '7s' })}>
          <circle cx="96" cy={50 + i * 26} r="7" fill={f.c} fillOpacity="0.85" />
          <text x="110" y={54 + i * 26} fontSize="9.5" fill="#cbd5e1">
            {f.t}
          </text>
        </g>
      ))}
      {/* files dropping into the shared folder */}
      <rect x="226" y="48" width="78" height="112" rx="8" fill="#fff" fillOpacity="0.05" stroke="#fff" strokeOpacity="0.12" strokeDasharray="4 4" />
      <text x="265" y="64" fontSize="8.5" textAnchor="middle" fill="#94a3b8">
        Files
      </text>
      {[0, 1, 2].map((i) => (
        <g key={i} {...anim('ba-drop', 0.8 + i * 1.1, { '--d': '7s' })}>
          <path d={`M${240} ${74 + i * 28}h30l8 8v16h-38z`} fill={[C.cyan, C.violet, C.mint][i]} fillOpacity="0.8" />
          <rect x="246" y={86 + i * 28} width="18" height="3" rx="1.5" fill="#0f172a" fillOpacity="0.5" />
        </g>
      ))}
      <defs>
        <linearGradient id="lp-av" x1="0" x2="1">
          <stop offset="0" stopColor={C.cyan} />
          <stop offset="1" stopColor={C.violet} />
        </linearGradient>
      </defs>
    </Svg>
  )
}

/** Reliable delivery — days tick off on time, the delivery day lands. */
function OnTimeCalendar() {
  const cells = Array.from({ length: 14 })
  return (
    <Svg vb="0 0 320 110">
      <rect x="40" y="6" width="240" height="98" rx="8" fill="#fff" fillOpacity="0.05" stroke="#fff" strokeOpacity="0.12" />
      <rect x="40" y="6" width="240" height="18" rx="8" fill={C.cyan} fillOpacity="0.3" />
      {cells.map((_, i) => {
        const x = 50 + (i % 7) * 32
        const y = 32 + Math.floor(i / 7) * 34
        const last = i === 13
        return (
          <g key={i}>
            <rect x={x} y={y} width="26" height="28" rx="4" fill={last ? C.amber : '#fff'} fillOpacity={last ? 0.25 : 0.06} stroke={last ? C.amber : 'none'} />
            {!last && (
              <path
                d={`M${x + 7} ${y + 14}l4 4 8-9`}
                stroke={C.mint}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                pathLength={100}
                {...anim('ba-draw', i * 0.28, { '--d': '6s' })}
              />
            )}
            {last && (
              <g {...anim('ba-stamp', 3.6, { '--d': '6s' }, `${x + 13}px ${y + 14}px`)}>
                <path d={`M${x + 9} ${y + 6}v18`} stroke={C.amber} strokeWidth="2" strokeLinecap="round" />
                <path d={`M${x + 10} ${y + 6}h10l-3 4 3 4h-10z`} fill={C.amber} />
              </g>
            )}
          </g>
        )
      })}
    </Svg>
  )
}

/** A team that listens — your words come in, the team's sound bars respond. */
function Listening() {
  const bars = Array.from({ length: 12 })
  return (
    <Svg vb="0 0 320 110">
      <circle cx="40" cy="50" r="16" fill={C.violet} fillOpacity="0.85" />
      <path d="M18 92a22 18 0 0 1 44 0z" fill={C.violet} fillOpacity="0.85" />
      <rect x="70" y="20" width="180" height="62" rx="18" fill="#fff" fillOpacity="0.07" stroke="#fff" strokeOpacity="0.15" />
      {bars.map((_, i) => (
        <rect
          key={i}
          x={88 + i * 13}
          y="31"
          width="7"
          height="40"
          rx="3.5"
          fill={i % 2 ? C.cyan : C.violet}
          {...anim('ba-eq', i * 0.09, { '--d': `${0.45 + (i % 4) * 0.12}s` }, `${91.5 + i * 13}px 51px`)}
        />
      ))}
      <circle cx="280" cy="50" r="16" fill={C.cyan} fillOpacity="0.85" />
      <path d="M258 92a22 18 0 0 1 44 0z" fill={C.cyan} fillOpacity="0.85" />
      <g {...anim('ba-pop', 1.2, { '--d': '4s' })}>
        <rect x="256" y="8" width="48" height="18" rx="9" fill={C.mint} />
        <text x="280" y="21" textAnchor="middle" fontSize="9" fontWeight="800" fill="#04261a">
          Got it!
        </text>
      </g>
    </Svg>
  )
}

/** Built to scale — blocks drop in and the structure keeps growing. */
function StackingBlocks() {
  const blocks = [
    { x: 100, y: 86, w: 120 },
    { x: 108, y: 66, w: 104 },
    { x: 116, y: 46, w: 88 },
    { x: 124, y: 26, w: 72 },
    { x: 140, y: 6, w: 40 },
  ]
  const colors = [C.cyan, C.violet, C.mint, C.sky, C.amber]
  return (
    <Svg vb="0 0 320 110">
      <path d="M60 106 H260" stroke="#fff" strokeOpacity="0.25" strokeWidth="2" />
      {blocks.map((b, i) => (
        <g key={i} {...anim('ba-drop', i * 0.55, { '--d': '6s' })}>
          <rect x={b.x} y={b.y} width={b.w} height="18" rx="3" fill={colors[i]} fillOpacity="0.85" />
          <rect x={b.x + 6} y={b.y + 7} width={b.w * 0.4} height="4" rx="2" fill="#0f172a" fillOpacity="0.35" />
        </g>
      ))}
      <path d="M262 92 V22" stroke={C.mint} strokeWidth="2.5" strokeLinecap="round" />
      <path d="M255 30 L262 20 L269 30" stroke={C.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" {...anim('ba-float', 0, { '--d': '1.6s' })} />
    </Svg>
  )
}

/** Transparent pricing — the quote prints line by line and gets approved. */
function ClearQuote() {
  return (
    <Svg vb="0 0 320 110">
      <defs>
        <clipPath id="cq-slot">
          <rect x="90" y="20" width="140" height="90" />
        </clipPath>
      </defs>
      <rect x="80" y="8" width="160" height="16" rx="6" fill="#334155" />
      <rect x="92" y="14" width="136" height="4" rx="2" fill="#0f172a" />
      <g clipPath="url(#cq-slot)">
        <g {...anim('ba-print', 0, { '--d': '6s' })}>
          <path d="M100 16 H220 V100 l-10 6 -10 -6 -10 6 -10 -6 -10 6 -10 -6 -10 6 -10 -6 -10 6 -10 -6 -10 6 -10 -6 z" fill="#f8fafc" />
          {[0, 1, 2].map((i) => (
            <g key={i}>
              <rect x="110" y={30 + i * 14} width="56" height="4" rx="2" fill="#64748b" />
              <rect x="190" y={30 + i * 14} width="20" height="4" rx="2" fill="#64748b" />
            </g>
          ))}
          <path d="M110 74 H210" stroke="#cbd5e1" strokeDasharray="3 3" />
          <rect x="110" y="82" width="34" height="6" rx="3" fill="#0f172a" />
          <rect x="182" y="82" width="28" height="6" rx="3" fill={C.cyan} />
        </g>
      </g>
      <g {...anim('ba-stamp', 2.4, { '--d': '6s' }, '262px 70px')}>
        <rect x="236" y="56" width="74" height="28" rx="6" stroke={C.mint} strokeWidth="3" fill={C.mint} fillOpacity="0.1" />
        <text x="273" y="75" textAnchor="middle" fontSize="11" fontWeight="900" fill={C.mint} letterSpacing="1">
          APPROVED
        </text>
      </g>
    </Svg>
  )
}

const WHY = { portal: LivePortal, delivery: OnTimeCalendar, listen: Listening, scale: StackingBlocks, pricing: ClearQuote } satisfies Record<
  string,
  () => JSX.Element
>
export type WhyKind = keyof typeof WHY
export function WhyArt({ kind }: { kind: WhyKind }) {
  const Art = WHY[kind]
  return <Art />
}

// ---------------------------------------------------------------------------
// From idea to working technology
// ---------------------------------------------------------------------------

/**
 * One laptop whose screen changes with the stage: sticky notes (Planning),
 * wireframe (Design), code (Development), upload to the cloud (Deployment),
 * a support chat (Support). 10s cycle, 2s per stage — the stage chips beside
 * it use the same timing (`.stage-chip`), so the two stay in step.
 */
export function IdeaToTechArt() {
  const stage = (i: number) => anim('ba-stage', i * 2, { '--d': '10s' })
  return (
    <Svg vb="0 0 360 260">
      <defs>
        <clipPath id="itt-screen">
          <rect x="50" y="30" width="260" height="160" rx="6" />
        </clipPath>
        <linearGradient id="itt-glow" x1="0" x2="1">
          <stop offset="0" stopColor={C.cyan} />
          <stop offset="1" stopColor={C.violet} />
        </linearGradient>
      </defs>
      <ellipse cx="180" cy="236" rx="160" ry="14" fill={C.cyan} fillOpacity="0.12" />
      <rect x="40" y="20" width="280" height="180" rx="12" fill="#0b1120" stroke="url(#itt-glow)" strokeWidth="2.5" />
      <path d="M14 206 H346 L328 226 H32 Z" fill="#1e293b" stroke="#334155" />
      <rect x="150" y="208" width="60" height="6" rx="3" fill="#334155" />
      <g clipPath="url(#itt-screen)">
        <rect x="50" y="30" width="260" height="160" fill="#020617" />

        {/* 1 Planning — sticky notes */}
        <g {...stage(0)}>
          {[
            [70, 50, C.amber, -4], [150, 46, C.pink, 3], [228, 52, C.mint, -2], [96, 116, C.sky, 2], [182, 112, C.violet, -3],
          ].map(([x, y, c, r], i) => (
            <g key={i} transform={`rotate(${r} ${(x as number) + 32} ${(y as number) + 28})`}>
              <rect x={x as number} y={y as number} width="64" height="56" rx="4" fill={c as string} fillOpacity="0.85" />
              <rect x={(x as number) + 8} y={(y as number) + 14} width="40" height="4" rx="2" fill="#0f172a" fillOpacity="0.45" />
              <rect x={(x as number) + 8} y={(y as number) + 24} width="30" height="4" rx="2" fill="#0f172a" fillOpacity="0.3" />
            </g>
          ))}
        </g>

        {/* 2 Design — wireframe drawing */}
        <g {...stage(1)}>
          {[
            'M66 46 H294', 'M66 60 H294', 'M66 74 H170 V140 H66 Z', 'M186 74 H294 V100 H186 Z', 'M186 110 H294 V140 H186 Z', 'M66 154 H130 V174 H66 Z',
          ].map((d, i) => (
            <path key={i} d={d} stroke={C.sky} strokeWidth="2" strokeDasharray="5 4" />
          ))}
          <path d="M66 74 L170 140 M170 74 L66 140" stroke={C.sky} strokeOpacity="0.4" />
        </g>

        {/* 3 Development — code lines */}
        <g {...stage(2)}>
          {[
            [0, 120, C.violet], [16, 160, '#e2e8f0'], [32, 90, C.cyan], [32, 140, '#e2e8f0'], [48, 70, C.mint], [16, 110, '#e2e8f0'], [0, 40, C.violet],
          ].map(([ind, w, c], i) => (
            <rect key={i} x={70 + (ind as number)} y={48 + i * 18} width={w as number} height="7" rx="3.5" fill={c as string} fillOpacity="0.85" />
          ))}
          <rect x="70" y="174" width="8" height="10" fill={C.mint} />
        </g>

        {/* 4 Deployment — upload to the cloud */}
        <g {...stage(3)}>
          <path d="M140 110 a26 26 0 0 1 50 -10 a20 20 0 0 1 36 16 a16 16 0 0 1 -6 30 H146 a20 20 0 0 1 -6 -36z" fill={C.cyan} fillOpacity="0.18" stroke={C.cyan} strokeWidth="2" />
          <path d="M180 140 V108 M168 120 L180 108 L192 120" stroke="#fff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
          <rect x="90" y="166" width="180" height="8" rx="4" fill="#fff" fillOpacity="0.1" />
          <rect x="90" y="166" width="180" height="8" rx="4" fill="url(#itt-glow)" />
        </g>

        {/* 5 Support — chat */}
        <g {...stage(4)}>
          <rect x="70" y="52" width="150" height="34" rx="12" fill="#fff" fillOpacity="0.12" />
          <rect x="82" y="64" width="110" height="5" rx="2.5" fill="#cbd5e1" />
          <rect x="82" y="73" width="70" height="5" rx="2.5" fill="#cbd5e1" fillOpacity="0.6" />
          <rect x="140" y="100" width="150" height="34" rx="12" fill={C.mint} fillOpacity="0.85" />
          <rect x="152" y="112" width="96" height="5" rx="2.5" fill="#04261a" fillOpacity="0.6" />
          <rect x="152" y="121" width="60" height="5" rx="2.5" fill="#04261a" fillOpacity="0.45" />
          <circle cx="280" cy="160" r="12" fill={C.mint} />
          <path d="M274 160l4 4 8-9" stroke="#04261a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </g>
      </g>
      {/* progress dots under the laptop */}
      {Array.from({ length: 5 }).map((_, i) => (
        <g key={i}>
          <circle cx={140 + i * 20} cy="250" r="4" fill="#fff" fillOpacity="0.2" />
          <circle cx={140 + i * 20} cy="250" r="4" fill="url(#itt-glow)" {...stage(i)} />
        </g>
      ))}
    </Svg>
  )
}
