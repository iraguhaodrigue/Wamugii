import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, Cpu, Globe, Layers, Lightbulb, ShieldCheck, Sparkles, Users, Zap } from 'lucide-react'
import { listServices } from '@/api/services'
import { paths } from '@/routes/paths'
import { Container, EmptyState, ErrorState } from '@/components/ui'
import { ServiceCard } from '@/components/services/ServiceCard'
import { ServiceCardSkeleton } from '@/components/services/ServiceCardSkeleton'

const valueProps = [
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

const techPillars = [
  {
    icon: Cpu,
    title: 'Modern engineering',
    description: 'Current frameworks and tooling, chosen for maintainability, not hype.',
  },
  {
    icon: ShieldCheck,
    title: 'Secure by default',
    description: 'Authentication, data handling, and infrastructure built with security as a first-class concern.',
  },
  {
    icon: Layers,
    title: 'Scalable architecture',
    description: 'Systems designed to grow from your first users to your busiest day.',
  },
  {
    icon: Globe,
    title: 'End-to-end support',
    description: 'From first consultation to post-launch support — one team, one point of contact.',
  },
]

export function Home() {
  const {
    data: services,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['services', 'home-preview'],
    queryFn: () => listServices(),
  })

  const preview = services?.slice(0, 6) ?? []

  return (
    <>
      <section className="relative overflow-hidden bg-gradient-to-br from-brand-950 to-brand-900">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.15]"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
            backgroundSize: '32px 32px',
          }}
          aria-hidden="true"
        />
        <Container className="relative py-24 sm:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-accent-200 ring-1 ring-inset ring-white/20">
              <Sparkles className="size-3.5" aria-hidden="true" />
              Technology partner for growing businesses
            </span>
            <h1 className="mt-6 text-4xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
              WAMUGII TECH SOLUTIONS
            </h1>
            <p className="mt-4 text-xl font-medium text-brand-100 sm:text-2xl">We Build. We Innovate. We Empower.</p>
            <p className="mx-auto mt-6 max-w-xl text-base text-brand-100/90">
              We design, build, and support the software, websites, and IT systems that power your business — end
              to end.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Link
                to={paths.services}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-white px-6 text-sm font-semibold text-brand-900 shadow-lg shadow-black/10 transition-colors hover:bg-brand-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-900 sm:w-auto"
              >
                Explore Services
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
              <Link
                to={paths.requestQuote}
                className="inline-flex h-12 w-full items-center justify-center rounded-lg border border-white/30 px-6 text-sm font-semibold text-white transition-colors hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-brand-900 sm:w-auto"
              >
                Request a Quote
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-24">
        <Container>
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">What we do</h2>
            <p className="mt-3 text-base text-slate-500">
              A focused set of services covering the full lifecycle of your technology needs.
            </p>
          </div>

          <div className="mt-12">
            {isLoading && (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <ServiceCardSkeleton key={i} />
                ))}
              </div>
            )}

            {isError && !isLoading && (
              <ErrorState
                title="Couldn't load services"
                message="We had trouble reaching the server. Please try again."
                onRetry={() => refetch()}
              />
            )}

            {!isLoading && !isError && preview.length === 0 && (
              <EmptyState title="No services published yet" description="Check back soon — we're setting things up." />
            )}

            {!isLoading && !isError && preview.length > 0 && (
              <>
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {preview.map((service) => (
                    <ServiceCard key={service.id} service={service} />
                  ))}
                </div>
                {services && services.length > preview.length && (
                  <div className="mt-10 text-center">
                    <Link
                      to={paths.services}
                      className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
                    >
                      View all services
                      <ArrowRight className="size-4" aria-hidden="true" />
                    </Link>
                  </div>
                )}
              </>
            )}
          </div>
        </Container>
      </section>

      <section className="bg-slate-900 py-20 sm:py-24">
        <Container>
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">Why choose WAMUGII</h2>
            <p className="mt-3 text-base text-slate-400">We act as an extension of your team, not just a vendor.</p>
          </div>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {valueProps.map(({ icon: Icon, title, description }) => (
              <div key={title} className="rounded-xl border border-white/10 bg-white/5 p-6">
                <div className="flex size-10 items-center justify-center rounded-lg bg-brand-500/15 text-brand-400">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
                <h3 className="mt-4 text-base font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm text-slate-400">{description}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-24">
        <Container>
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <span className="text-sm font-semibold uppercase tracking-wide text-brand-600">
                Technology &amp; Innovation
              </span>
              <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                Engineering built for the long run
              </h2>
              <p className="mt-4 text-base text-slate-500">
                We invest in solid foundations — clean architecture, secure defaults, and infrastructure that
                scales — so what we build for you keeps paying off long after launch.
              </p>
              <Link
                to={paths.requestQuote}
                className="mt-8 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
              >
                Start a conversation
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
              {techPillars.map(({ icon: Icon, title, description }) => (
                <div key={title} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <div className="flex size-10 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
                    <Icon className="size-5" aria-hidden="true" />
                  </div>
                  <h3 className="mt-3 text-sm font-semibold text-slate-900">{title}</h3>
                  <p className="mt-1.5 text-sm text-slate-500">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </Container>
      </section>
    </>
  )
}
