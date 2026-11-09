import type { CSSProperties } from 'react'
import { Code, Cpu, Globe, Layers, Lightbulb, Search, Server, Sparkles, Wifi, type LucideIcon } from 'lucide-react'
import { AnimInView } from './AnimInView'

/**
 * Header illustrations for the inner public pages — each drawn for its page:
 *
 *  * ServicesOrbit — our services orbiting the WAMUGII core
 *  * HostingArt    — a live rack sending data to the cloud, domains being found
 *  * DomainArt     — a browser address bar trying extensions until one is free
 *  * QuoteArt      — your request flies, as a paper plane, into our inbox
 *  * AuthArt       — a fingerprint scan opens your client portal
 *
 * All motion is CSS (`.pg-*` and the shared `.ba-*` classes in index.css),
 * runs only while on screen (AnimInView) and stops under reduced motion.
 */

function a(cls: string, delay = 0, vars: Record<string, string> = {}, origin?: string) {
  const style: Record<string, string> = { animationDelay: `${delay}s`, ...vars }
  if (origin) style.transformOrigin = origin
  return { className: cls, style: style as CSSProperties }
}

const C = { cyan: '#22d3ee', violet: '#a78bfa', mint: '#34d399', amber: '#fbbf24', pink: '#f472b6' }

// ---------------------------------------------------------------------------

const INNER: { icon: LucideIcon; c: string }[] = [
  { icon: Globe, c: C.cyan },
  { icon: Code, c: C.violet },
  { icon: Server, c: C.mint },
  { icon: Lightbulb, c: C.amber },
]
const OUTER: { icon: LucideIcon; c: string }[] = [
  { icon: Wifi, c: C.cyan },
  { icon: Search, c: C.pink },
  { icon: Cpu, c: C.mint },
  { icon: Layers, c: C.violet },
  { icon: Sparkles, c: C.amber },
]

function Ring({ items, radius, cls }: { items: { icon: LucideIcon; c: string }[]; radius: number; cls: string }) {
  return (
    <div className={`pg-ring absolute inset-0 ${cls}`}>
      {items.map(({ icon: Icon, c }, i) => {
        const angle = (360 / items.length) * i
        return (
          <div
            key={i}
            className="absolute left-1/2 top-1/2"
            style={{ transform: `rotate(${angle}deg) translateX(${radius}px) rotate(${-angle}deg)` }}
          >
            <div className={`pg-ring-counter ${cls}`}>
              <div
                className="-ml-6 -mt-6 flex size-12 items-center justify-center rounded-2xl border border-white/15 bg-[#0b1726]/90 shadow-lg backdrop-blur"
                style={{ boxShadow: `0 0 24px -6px ${c}` }}
              >
                <Icon className="size-5" style={{ color: c }} aria-hidden="true" />
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export function ServicesOrbit() {
  return (
    <AnimInView className="relative mx-auto aspect-square w-full max-w-[380px]">
      <div className="absolute inset-[18%] rounded-full border border-dashed border-cyan-300/25" />
      <div className="absolute inset-[3%] rounded-full border border-violet-300/15" />
      <Ring items={INNER} radius={115} cls="pg-ring-a" />
      <Ring items={OUTER} radius={172} cls="pg-ring-b" />
      <div className="absolute left-1/2 top-1/2 -ml-14 -mt-14 flex size-28 items-center justify-center">
        <span className="pg-core-ping absolute inset-0 rounded-full bg-cyan-400/25" />
        <span className="absolute inset-2 rounded-full bg-gradient-to-br from-cyan-500 to-violet-600 shadow-[0_0_60px_-10px_rgb(34_211_238/0.8)]" />
        <img src="/logo-emblem-128.png" alt="" className="relative size-16 rounded-full object-cover ring-2 ring-white/30" />
      </div>
    </AnimInView>
  )
}

// ---------------------------------------------------------------------------

export function HostingArt() {
  const domains = ['yourbusiness.rw', 'myshop.africa', 'company.com']
  return (
    <AnimInView className="w-full">
      <svg viewBox="0 0 360 260" className="h-auto w-full" fill="none">
        {/* rack */}
        <rect x="20" y="40" width="130" height="190" rx="12" fill="#0b1726" stroke="#fff" strokeOpacity="0.15" />
        {Array.from({ length: 5 }).map((_, i) => (
          <g key={i}>
            <rect x="32" y={54 + i * 34} width="106" height="26" rx="5" fill="#fff" fillOpacity="0.06" stroke="#fff" strokeOpacity="0.1" />
            {[0, 1, 2].map((j) => (
              <rect key={j} x={40 + j * 8} y={63 + i * 34} width="4" height="8" rx="1" fill="#94a3b8" fillOpacity="0.5" />
            ))}
            <rect x="72" y={65 + i * 34} width="36" height="4" rx="2" fill="#fff" fillOpacity="0.1" />
            <rect x="72" y={65 + i * 34} width="36" height="4" rx="2" fill={C.cyan} {...a('ba-grow', i * 0.4, { '--d': '2.6s' }, `72px ${67 + i * 34}px`)} />
            <circle cx="120" cy={67 + i * 34} r="3.5" fill={C.mint} {...a('ba-blink', i * 0.25, { '--d': '0.8s' })} />
            <circle cx="129" cy={67 + i * 34} r="3.5" fill={C.violet} {...a('ba-blink', 0.5 + i * 0.2, { '--d': '1.3s' })} />
          </g>
        ))}
        {/* data to the cloud */}
        <path d="M150 90 C 200 90, 210 60, 248 60" stroke={C.cyan} strokeOpacity="0.5" strokeWidth="2" strokeDasharray="5 6" {...a('ba-flow', 0, { '--d': '0.9s', '--dash-end': '-11' })} />
        <path d="M150 150 C 210 150, 220 80, 262 74" stroke={C.violet} strokeOpacity="0.5" strokeWidth="2" strokeDasharray="5 6" {...a('ba-flow', 0.3, { '--d': '1.1s', '--dash-end': '-11' })} />
        <g {...a('ba-float', 0, { '--d': '5s' })}>
          <path d="M238 70 a24 24 0 0 1 44 -12 a18 18 0 0 1 34 12 a15 15 0 0 1 -4 30 H242 a17 17 0 0 1 -4 -30z" fill={C.cyan} fillOpacity="0.15" stroke={C.cyan} strokeWidth="2" />
          <text x="277" y="86" textAnchor="middle" fontSize="11" fontWeight="800" fill="#a5f3fc">
            ONLINE
          </text>
        </g>
        <circle cx="330" cy="40" r="6" fill={C.mint} />
        <circle cx="330" cy="40" r="6" fill={C.mint} {...a('ba-ping', 0, { '--d': '2s' }, '330px 40px')} />
        {/* domain search */}
        <rect x="170" y="176" width="176" height="40" rx="20" fill="#fff" fillOpacity="0.08" stroke="#fff" strokeOpacity="0.2" />
        <circle cx="191" cy="196" r="6" stroke="#cbd5e1" strokeWidth="2" />
        <path d="M195 200l5 5" stroke="#cbd5e1" strokeWidth="2" strokeLinecap="round" />
        {domains.map((d, i) => (
          <g key={d} {...a('pg-cycle3', i * 3)}>
            <text x="208" y="201" fontSize="12" fontWeight="600" fill="#e2e8f0">
              {d}
            </text>
          </g>
        ))}
        <g {...a('pg-cycle3-late', 0)}>
          <rect x="250" y="226" width="96" height="22" rx="11" fill={C.mint} fillOpacity="0.2" stroke={C.mint} strokeOpacity="0.7" />
          <text x="298" y="241" textAnchor="middle" fontSize="10" fontWeight="800" fill={C.mint}>
            ✓ Available
          </text>
        </g>
      </svg>
    </AnimInView>
  )
}

export function DomainArt() {
  const tries = [
    { ext: '.rw', ok: true },
    { ext: '.co.rw', ok: true },
    { ext: '.com', ok: false },
  ]
  return (
    <AnimInView className="w-full">
      <svg viewBox="0 0 360 260" className="h-auto w-full" fill="none">
        {/* browser window */}
        <rect x="16" y="34" width="328" height="192" rx="16" fill="#0b1726" stroke="#fff" strokeOpacity="0.15" />
        <circle cx="38" cy="56" r="5" fill="#f472b6" />
        <circle cx="54" cy="56" r="5" fill={C.amber} />
        <circle cx="70" cy="56" r="5" fill={C.mint} />
        <rect x="34" y="78" width="292" height="44" rx="22" fill="#fff" fillOpacity="0.08" stroke="#fff" strokeOpacity="0.2" />
        <path d="M54 94 a6 6 0 0 1 12 0 v3 h2 v10 h-16 v-10 h2z" stroke={C.mint} strokeWidth="1.8" />
        <text x="80" y="106" fontSize="17" fontWeight="700" fill="#e2e8f0">
          yourname
        </text>
        {tries.map((t, i) => (
          <g key={t.ext} {...a('pg-cycle3', i * 3)}>
            <text x="163" y="106" fontSize="17" fontWeight="800" fill={C.cyan}>
              {t.ext}
            </text>
            <rect x="214" y="142" width="112" height="26" rx="13" fill={t.ok ? C.mint : '#94a3b8'} fillOpacity="0.18"
              stroke={t.ok ? C.mint : '#94a3b8'} strokeOpacity="0.7" />
            <text x="270" y="159" textAnchor="middle" fontSize="11" fontWeight="800" fill={t.ok ? C.mint : '#cbd5e1'}>
              {t.ok ? '\u2713 Available' : 'Taken'}
            </text>
          </g>
        ))}
        {/* page skeleton */}
        <rect x="34" y="142" width="150" height="10" rx="5" fill="#fff" fillOpacity="0.12" />
        <rect x="34" y="162" width="110" height="10" rx="5" fill="#fff" fillOpacity="0.08" />
        <rect x="34" y="190" width="292" height="18" rx="9" fill={C.cyan} fillOpacity="0.12" {...a('ba-grow', 0, { '--d': '3s' }, '34px 199px')} />
        <circle cx="326" cy="28" r="7" fill={C.mint} />
        <circle cx="326" cy="28" r="7" fill={C.mint} {...a('ba-ping', 0, { '--d': '2s' }, '326px 28px')} />
      </svg>
    </AnimInView>
  )
}

// ---------------------------------------------------------------------------

const PLANE_PATH = "path('M70 150 C 120 40, 210 40, 250 110 S 300 170, 312 128')"

export function QuoteArt() {
  return (
    <AnimInView className="w-full">
      <svg viewBox="0 0 360 240" className="h-auto w-full" fill="none">
        {/* the form */}
        <rect x="16" y="86" width="110" height="138" rx="10" fill="#fff" fillOpacity="0.92" />
        <rect x="28" y="100" width="54" height="7" rx="3.5" fill="#0f172a" fillOpacity="0.7" />
        {[0, 1, 2, 3].map((i) => (
          <g key={i}>
            <rect x="28" y={118 + i * 22} width="86" height="14" rx="4" fill="#e2e8f0" />
            <rect x="32" y={123 + i * 22} width={[60, 40, 70, 50][i]} height="4" rx="2" fill={C.cyan} {...a('ba-grow', i * 0.35, { '--d': '5s' }, `32px ${125 + i * 22}px`)} />
          </g>
        ))}
        {/* flight path */}
        <path d="M70 150 C 120 40, 210 40, 250 110 S 300 170, 312 128" stroke="#fff" strokeOpacity="0.25" strokeWidth="2" strokeDasharray="4 7" />
        {/* inbox */}
        <g>
          <path d="M276 120 h72 v56 a8 8 0 0 1 -8 8 h-56 a8 8 0 0 1 -8 -8z" fill="#0b1726" stroke={C.violet} strokeWidth="2" />
          <path d="M276 150 h20 l6 10 h20 l6 -10 h20" stroke={C.violet} strokeWidth="2" strokeLinejoin="round" />
        </g>
        <g className="pg-plane" style={{ offsetPath: PLANE_PATH } as CSSProperties}>
          <path d="M-14 -8 L16 0 L-14 8 L-8 0 Z" fill="#fff" />
          <path d="M-8 0 L16 0" stroke="#94a3b8" strokeWidth="1" />
        </g>
        <g {...a('pg-sent')}>
          <rect x="232" y="196" width="118" height="30" rx="15" fill={C.mint} />
          <text x="291" y="215" textAnchor="middle" fontSize="11" fontWeight="800" fill="#04261a">
            ✓ Request sent
          </text>
        </g>
      </svg>
    </AnimInView>
  )
}

// ---------------------------------------------------------------------------

export function AuthArt() {
  const arcs = [14, 24, 34, 44, 54]
  const features = ['Track your projects live', 'Download invoices & files', 'Continue your courses']
  return (
    <AnimInView className="w-full">
      <svg viewBox="0 0 360 320" className="h-auto w-full" fill="none">
        <defs>
          <clipPath id="auth-fp">
            <circle cx="180" cy="104" r="64" />
          </clipPath>
        </defs>
        <circle cx="180" cy="104" r="76" fill="#22d3ee" fillOpacity="0.06" stroke="#22d3ee" strokeOpacity="0.25" />
        {arcs.map((r, i) => (
          <path
            key={r}
            d={`M ${180 - r} ${114} A ${r} ${r + 6} 0 0 1 ${180 + r} ${114}`}
            stroke={i % 2 ? C.violet : C.cyan}
            strokeWidth="3.5"
            strokeLinecap="round"
            pathLength={100}
            {...a('ba-draw', i * 0.15, { '--d': '6s' })}
          />
        ))}
        <path d="M180 92 V140" stroke={C.cyan} strokeWidth="3.5" strokeLinecap="round" pathLength={100} {...a('ba-draw', 0.8, { '--d': '6s' })} />
        <g clipPath="url(#auth-fp)">
          <rect x="110" y="36" width="140" height="10" fill={C.cyan} fillOpacity="0.55" className="pg-scan" />
        </g>
        <g {...a('pg-unlock')}>
          <circle cx="234" cy="52" r="16" fill={C.mint} />
          <path d="M226 52l5 5 10-11" stroke="#04261a" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </g>
        {features.map((f, i) => (
          <g key={f} {...a('pg-feature', i * 0.35)}>
            <rect x="54" y={200 + i * 38} width="252" height="30" rx="10" fill="#fff" fillOpacity="0.07" stroke="#fff" strokeOpacity="0.12" />
            <circle cx="74" cy={215 + i * 38} r="7" fill={[C.cyan, C.violet, C.mint][i]} />
            <text x="90" y={219 + i * 38} fontSize="12" fill="#e2e8f0" fontWeight="600">
              {f}
            </text>
          </g>
        ))}
      </svg>
    </AnimInView>
  )
}
