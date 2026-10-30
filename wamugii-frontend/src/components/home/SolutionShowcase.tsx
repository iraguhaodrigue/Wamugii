import { Link } from 'react-router-dom'
import { ArrowRight, Boxes, Globe, Network, Server, ShoppingCart, Workflow } from 'lucide-react'
import { paths } from '@/routes/paths'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { cn } from '@/utils/cn'
import { SectionHeading } from './SectionHeading'
import { AnimInView } from '@/components/common/AnimInView'
import { SolutionArt, type SolutionKind } from './BusinessArt'

/*
 * The visuals (BusinessArt) are abstract animated UI motifs — deliberately *not*
 * screenshots or mockups of client work, since presenting invented project
 * imagery as real would misrepresent the business. They suggest the shape of
 * each solution type without claiming a specific build.
 */

interface Solution {
  icon: typeof Globe
  title: string
  description: string
  art: SolutionKind
  span: string
}

const solutions: Solution[] = [
  {
    icon: Globe,
    title: 'Business websites',
    description:
      'A professional online presence that loads fast, works on phones, and is easy for your team to keep updated.',
    art: 'website',
    span: 'lg:col-span-4',
  },
  {
    icon: Boxes,
    title: 'Management systems',
    description: 'Custom internal tools that replace the spreadsheets your business has outgrown.',
    art: 'management',
    span: 'lg:col-span-2',
  },
  {
    icon: ShoppingCart,
    title: 'E-commerce',
    description: 'Online storefronts with catalogues, orders and payments handled properly.',
    art: 'ecommerce',
    span: 'lg:col-span-2',
  },
  {
    icon: Workflow,
    title: 'Business automation',
    description:
      'Repetitive processes turned into software — less manual data entry, fewer mistakes, and hours given back to your team.',
    art: 'automation',
    span: 'lg:col-span-4',
  },
  {
    icon: Server,
    title: 'Hosting & domains',
    description: 'Somewhere reliable for your systems to live, set up and looked after for you.',
    art: 'hosting',
    span: 'lg:col-span-3',
  },
  {
    icon: Network,
    title: 'IT infrastructure',
    description: 'Installation, configuration and consultancy for the systems your office runs on.',
    art: 'network',
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
          {solutions.map(({ icon: Icon, title, description, art, span }, index) => (
            <Reveal key={title} delay={index * 70} className={cn('h-full', span)}>
              <div className="group flex h-full flex-col rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/30 hover:bg-white/[0.07]">
                <div className="icon-live flex size-10 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-400">{description}</p>
                <AnimInView className="mt-5 h-36 rounded-xl border border-white/10 bg-black/30 p-2">
                  <SolutionArt kind={art} />
                </AnimInView>
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
