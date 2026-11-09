import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, BadgeCheck, FileText, Globe2, Search, ShieldCheck } from 'lucide-react'
import { listPublicExtensions } from '@/api/domains'
import { DomainArt } from '@/components/common/PageArt'
import { PageHeader } from '@/components/common/PageHeader'
import { DomainSearch } from '@/components/domains/DomainSearch'
import { Container, Skeleton } from '@/components/ui'
import { paths } from '@/routes/paths'
import { formatMoney } from '@/utils/format'

const STEPS = [
  { icon: Search, title: 'Search', text: 'Type a name. We ask each registry live whether it is free.' },
  { icon: FileText, title: 'Request it', text: 'Choose 1–5 years. Nothing is charged until you get our invoice.' },
  { icon: BadgeCheck, title: 'We register it', text: 'Our team registers it in your name and connects it to your site or email.' },
]

/** Public "find a domain" page: live availability search plus the price list. */
export function Domains() {
  const prices = useQuery({ queryKey: ['domains', 'extensions', 'public'], queryFn: listPublicExtensions })

  return (
    <>
      <PageHeader
        eyebrow="Domains"
        title="Find the right"
        highlight="domain name"
        description="Search .rw, .co.rw, .com and more. See instantly which names are free — checked live with each official registry — and get yours registered by our team."
        art={<DomainArt />}
      />

      <section className="py-10 sm:py-14">
        <Container className="max-w-4xl">
          <DomainSearch mode="public" />
        </Container>
      </section>

      <section className="border-t border-slate-200 py-12 sm:py-16">
        <Container className="grid gap-10 lg:grid-cols-[1.1fr_1fr]">
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">How it works</h2>
            <ol className="mt-6 space-y-5">
              {STEPS.map((s, i) => (
                <li key={s.title} className="flex gap-4">
                  <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-brand-500/10 tone-cyan">
                    <s.icon className="size-5" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="font-semibold text-slate-900">
                      {i + 1}. {s.title}
                    </p>
                    <p className="mt-1 text-sm text-slate-600">{s.text}</p>
                  </div>
                </li>
              ))}
            </ol>
            <div className="mt-8 rounded-2xl border border-slate-200 bg-panel p-5">
              <p className="flex items-center gap-2 font-semibold text-slate-900">
                <Globe2 className="size-5 tone-cyan" aria-hidden="true" /> Why a .rw domain?
              </p>
              <p className="mt-2 text-sm text-slate-600">
                .rw is Rwanda&apos;s own extension, run by RICTA. It tells customers you are a Rwandan business. Many
                companies also take the matching .com so nobody else can.
              </p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900">Prices per year</h2>
            <p className="mt-2 text-sm text-slate-600">Registration and our setup, in Rwandan francs.</p>
            <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-panel">
              {prices.isLoading ? (
                <div className="space-y-2 p-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={i} className="h-8" />
                  ))}
                </div>
              ) : (
                <table className="w-full text-sm">
                  <caption className="sr-only">Domain prices per year</caption>
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-600">
                      <th scope="col" className="px-5 py-3 font-semibold">Extension</th>
                      <th scope="col" className="px-5 py-3 text-right font-semibold">Per year</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(prices.data ?? []).map((p) => (
                      <tr key={p.extension} className="border-b border-slate-200 last:border-0">
                        <td className="px-5 py-3 font-semibold text-slate-900">{p.extension}</td>
                        <td className="px-5 py-3 text-right text-slate-700">{formatMoney(p.client_price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
            <p className="mt-4 flex items-start gap-2 text-sm text-slate-600">
              <ShieldCheck className="mt-0.5 size-4 shrink-0 tone-emerald" aria-hidden="true" />
              Need an extension that isn&apos;t listed, or hosting and email too?
            </p>
            <Link
              to={`${paths.requestQuote}?service=domain`}
              className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              Ask for a quote <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
          </div>
        </Container>
      </section>
    </>
  )
}
