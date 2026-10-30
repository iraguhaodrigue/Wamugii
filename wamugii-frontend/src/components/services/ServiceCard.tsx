import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { Service } from '@/api/services'
import { Badge } from '@/components/ui'
import { formatMoney } from '@/utils/format'
import { paths } from '@/routes/paths'
import { AnimInView } from '@/components/common/AnimInView'
import { ServiceArt } from '@/components/home/BusinessArt'

export function ServiceCard({ service }: { service: Service }) {
  const price = formatMoney(service.price_from)

  return (
    <Link
      to={paths.serviceDetail(service.id)}
      className="card-accent group relative flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all duration-200 hover:-translate-y-1 hover:border-brand-400/40 hover:shadow-[var(--shadow-glow-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      <div className="relative -mx-6 -mt-6 mb-5 overflow-hidden border-b border-white/10 bg-[#06131c]">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(400px_circle_at_20%_0%,rgb(34_211_238/0.22),transparent_60%),radial-gradient(400px_circle_at_90%_100%,rgb(124_58_237/0.2),transparent_60%)]"
          aria-hidden="true"
        />
        <AnimInView className="relative h-36 p-3 transition-transform duration-500 group-hover:scale-[1.04]">
          <ServiceArt name={service.name} />
        </AnimInView>
      </div>
      <h3 className="mt-0 text-lg font-semibold text-slate-900">{service.name}</h3>
      {service.short_description && (
        <p className="mt-2 line-clamp-3 text-sm text-slate-500">{service.short_description}</p>
      )}
      {service.category && (
        <div className="mt-4">
          <Badge variant="brand">{service.category}</Badge>
        </div>
      )}
      <div className="mt-auto flex items-center justify-between pt-5">
        <span className="text-sm font-medium text-slate-700">{price ? `From ${price}` : 'Contact for pricing'}</span>
        <span className="inline-flex items-center gap-1 text-sm font-medium text-brand-600">
          Learn more
          <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </span>
      </div>
    </Link>
  )
}
