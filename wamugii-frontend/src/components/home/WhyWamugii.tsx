import { Eye, Lightbulb, ShieldCheck, Users, Zap } from 'lucide-react'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'
import { AnimInView } from '@/components/common/AnimInView'
import { WhyArt, type WhyKind } from './TeamArt'

const lead = {
  icon: Eye,
  title: 'You can see the work as it happens',
  description:
    "Every project gets its own client portal. Milestones, progress and shared files are visible to you while the work is underway — so you never have to ask where things stand, and there is no gap between what we say and what you can check.",
}

const supporting = [
  {
    icon: ShieldCheck,
    art: 'delivery' as WhyKind,
    title: 'Reliable delivery',
    description: 'Clear milestones and honest timelines, so you always know where your project stands.',
  },
  {
    icon: Users,
    art: 'listen' as WhyKind,
    title: 'A team that listens',
    description: 'We start with your goals, not a template — every build is scoped around what you actually need.',
  },
  {
    icon: Zap,
    art: 'scale' as WhyKind,
    title: 'Built to scale',
    description: 'Solid engineering foundations that keep working as your business grows.',
  },
  {
    icon: Lightbulb,
    art: 'pricing' as WhyKind,
    title: 'Transparent pricing',
    description: 'No surprise invoices. You approve the scope and budget before we start.',
  },
]

export function WhyWamugii() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <div className="dot-texture pointer-events-none absolute inset-0 opacity-80" aria-hidden="true" />
      <Container className="relative">
        <SectionHeading
          label="Why WAMUGII"
          title="An extension of your team, not just a vendor"
          description="The difference shows up in how the work is run, not just what gets delivered."
        />

        <div className="mt-14 grid gap-5 lg:grid-cols-3">
          <Reveal className="lg:col-span-1">
            <div className="relative flex h-full flex-col justify-between overflow-hidden rounded-2xl border border-brand-400/20 bg-[var(--color-brand-950)] p-7 shadow-[var(--shadow-glow-brand)] sm:p-8">
              <div
                className="pointer-events-none absolute inset-0"
                style={{
                  background:
                    'radial-gradient(400px circle at 20% 0%, rgb(6 182 212 / 20%), transparent 65%), radial-gradient(400px circle at 100% 100%, rgb(124 58 237 / 18%), transparent 65%)',
                }}
                aria-hidden="true"
              />
              <div className="relative">
                <div className="icon-live flex size-12 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-brand-400">
                  <lead.icon className="size-6" aria-hidden="true" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">{lead.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate-400">{lead.description}</p>
              </div>
              <AnimInView className="relative mt-6 h-48 sm:h-56">
                <WhyArt kind="portal" />
              </AnimInView>
            </div>
          </Reveal>

          <div className="grid gap-5 sm:grid-cols-2 lg:col-span-2">
            {supporting.map(({ icon: Icon, art, title, description }, index) => (
              <Reveal key={title} delay={index * 70} className="h-full">
                <div className="card-accent group relative h-full overflow-hidden rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-brand-400/30 hover:shadow-[var(--shadow-glow-brand)]">
                  <AnimInView className="mb-5 h-28 overflow-hidden rounded-xl border border-white/10 bg-[#06131c] p-1.5 transition-transform duration-500 group-hover:scale-[1.03]">
                    <WhyArt kind={art} />
                  </AnimInView>
                  <div className="icon-live flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                    <Icon className="size-5" aria-hidden="true" />
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-slate-900">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-500">{description}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </Container>
    </section>
  )
}
