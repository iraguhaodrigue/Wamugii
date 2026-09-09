import { Eye, Lightbulb, ShieldCheck, Users, Zap } from 'lucide-react'
import { Container } from '@/components/ui'
import { Reveal } from '@/components/common/Reveal'
import { SectionHeading } from './SectionHeading'

const lead = {
  icon: Eye,
  title: 'You can see the work as it happens',
  description:
    "Every project gets its own client portal. Milestones, progress and shared files are visible to you while the work is underway — so you never have to ask where things stand, and there is no gap between what we say and what you can check.",
}

const supporting = [
  {
    icon: ShieldCheck,
    title: 'Reliable delivery',
    description: 'Clear milestones and honest timelines, so you always know where your project stands.',
  },
  {
    icon: Users,
    title: 'A team that listens',
    description: 'We start with your goals, not a template — every build is scoped around what you actually need.',
  },
  {
    icon: Zap,
    title: 'Built to scale',
    description: 'Solid engineering foundations that keep working as your business grows.',
  },
  {
    icon: Lightbulb,
    title: 'Transparent pricing',
    description: 'No surprise invoices. You approve the scope and budget before we start.',
  },
]

export function WhyWamugii() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-24">
      <Container>
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
                <div className="flex size-12 items-center justify-center rounded-xl border border-white/10 bg-white/5 text-brand-400">
                  <lead.icon className="size-6" aria-hidden="true" />
                </div>
                <h3 className="mt-6 text-xl font-semibold text-white">{lead.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-slate-400">{lead.description}</p>
              </div>
            </div>
          </Reveal>

          <div className="grid gap-5 sm:grid-cols-2 lg:col-span-2">
            {supporting.map(({ icon: Icon, title, description }, index) => (
              <Reveal key={title} delay={index * 70} className="h-full">
                <div className="h-full rounded-2xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/30">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
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
