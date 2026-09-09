import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Boxes, Globe, Network, Server, ShoppingCart, Workflow } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'
import { SectionHeading } from './SectionHeading'

/*
 * The visuals below are abstract UI motifs drawn in CSS — deliberately *not*
 * screenshots or mockups of client work, since presenting invented project
 * imagery as real would misrepresent the business. They suggest the shape of
 * each solution type without claiming a specific build.
 */

function BrowserMotif() {
  return (
    <div className="rounded-lg border border-white/10 bg-black/30 p-2.5">
      <div className="flex gap-1.5">
        <span className="size-1.5 rounded-full bg-brand-400/60" />
        <span className="size-1.5 rounded-full bg-accent-400/50" />
        <span className="size-1.5 rounded-full bg-white/20" />
      </div>
      <div className="mt-2.5 space-y-1.5">
        <div className="h-2 w-3/5 rounded bg-gradient-to-r from-brand-400/50 to-accent-400/30" />
        <div className="h-1.5 w-full rounded bg-white/10" />
        <div className="h-1.5 w-4/5 rounded bg-white/10" />
      </div>
    </div>
  )
}

function TableMotif() {
  return (
    <div className="space-y-1.5 rounded-lg border border-white/10 bg-black/30 p-2.5">
      {[0, 1, 2].map((row) => (
        <div key={row} className="flex items-center gap-2">
          <div className={cn('h-1.5 flex-1 rounded', row === 0 ? 'bg-brand-400/50' : 'bg-white/10')} />
          <div className="h-1.5 w-8 rounded bg-white/10" />
          <div className={cn('h-3 w-6 rounded-full', row === 0 ? 'bg-accent-400/40' : 'bg-white/10')} />
        </div>
      ))}
    </div>
  )
}

function GridMotif() {
  return (
    <div className="grid grid-cols-3 gap-1.5 rounded-lg border border-white/10 bg-black/30 p-2.5">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className={cn('h-6 rounded', i === 1 ? 'bg-gradient-to-br from-brand-400/50 to-accent-400/40' : 'bg-white/10')}
        />
      ))}
    </div>
  )
}

function FlowMotif() {
  return (
    <div className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-black/30 p-3">
      {[0, 1, 2].map((node) => (
        <div key={node} className="flex flex-1 items-center gap-1.5">
          <div className="size-2.5 shrink-0 rounded-full bg-brand-400/70" />
          {node < 2 && <div className="h-px flex-1 bg-gradient-to-r from-brand-400/50 to-accent-400/40" />}
        </div>
      ))}
      <div className="size-2.5 shrink-0 rounded-full bg-accent-400/70" />
    </div>
  )
}

function StackMotif() {
  return (
    <div className="space-y-1.5 rounded-lg border border-white/10 bg-black/30 p-2.5">
      {[0, 1, 2].map((layer) => (
        <div key={layer} className="flex items-center gap-2 rounded bg-white/5 px-2 py-1.5">
          <div className="size-1.5 rounded-full bg-brand-400/70" />
          <div className="h-1 flex-1 rounded bg-white/10" />
        </div>
      ))}
    </div>
  )
}

function NetworkMotif() {
  return (
    <div className="relative h-[76px] rounded-lg border border-white/10 bg-black/30 p-2.5">
      <svg className="size-full" viewBox="0 0 120 56" fill="none" aria-hidden="true">
        <line x1="20" y1="40" x2="60" y2="16" stroke="rgb(34 211 238 / 0.35)" strokeWidth="1" />
        <line x1="60" y1="16" x2="100" y2="40" stroke="rgb(167 139 250 / 0.35)" strokeWidth="1" />
        <line x1="20" y1="40" x2="100" y2="40" stroke="rgb(255 255 255 / 0.12)" strokeWidth="1" />
        <circle cx="60" cy="16" r="4" fill="rgb(34 211 238 / 0.7)" />
        <circle cx="20" cy="40" r="3" fill="rgb(255 255 255 / 0.35)" />
        <circle cx="100" cy="40" r="3" fill="rgb(167 139 250 / 0.7)" />
      </svg>
    </div>
  )
}

interface Solution {
  icon: typeof Globe
  title: string
  description: string
  motif: ReactNode
  span: string
}

const solutions: Solution[] = [
  {
    icon: Globe,
    title: 'Business websites',
    description:
      'A professional online presence that loads fast, works on phones, and is easy for your team to keep updated.',
    motif: <BrowserMotif />,
    span: 'lg:col-span-4',
  },
  {
    icon: Boxes,
    title: 'Management systems',
    description: 'Custom internal tools that replace the spreadsheets your business has outgrown.',
    motif: <TableMotif />,
    span: 'lg:col-span-2',
  },
  {
    icon: ShoppingCart,
    title: 'E-commerce',
    description: 'Online storefronts with catalogues, orders and payments handled properly.',
    motif: <GridMotif />,
    span: 'lg:col-span-2',
  },
  {
    icon: Workflow,
    title: 'Business automation',
    description:
      'Repetitive processes turned into software — less manual data entry, fewer mistakes, and hours given back to your team.',
    motif: <FlowMotif />,
    span: 'lg:col-span-4',
  },
  {
    icon: Server,
    title: 'Hosting & domains',
    description: 'Somewhere reliable for your systems to live, set up and looked after for you.',
    motif: <StackMotif />,
    span: 'lg:col-span-3',
  },
  {
    icon: Network,
    title: 'IT infrastructure',
    description: 'Installation, configuration and consultancy for the systems your office runs on.',
    motif: <NetworkMotif />,
    span: 'lg:col-span-3',
  },
]

export function SolutionShowcase() {
  return (
    <section className="relative overflow-hidden border-y border-slate-200 bg-black/30 py-20 sm:py-24">
      <div className="glow-pool-purple pointer-events-none absolute inset-0" aria-hidden="true" />
      <Container className="relative">
        <SectionHeading
          label="Solutions we build"
          title="Technology built around your business"
          description="Whatever shape the problem takes, the goal is the same — something practical that works for the way you actually operate."
        />

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-6">
          {solutions.map(({ icon: Icon, title, description, motif, span }, index) => (
            <Reveal key={title} delay={index * 70} className={cn('h-full', span)}>
              <div className="flex h-full flex-col rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/30 hover:bg-white/[0.07]">
                <div className="flex size-10 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{description}</p>
                <div className="mt-5">{motif}</div>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={100}>
          <div className="mt-10 text-center">
            <Link
              to={paths.services}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-400 hover:text-brand-300"
            >
              See all services
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>
        </Reveal>
      </Container>
    </section>
  )
}
