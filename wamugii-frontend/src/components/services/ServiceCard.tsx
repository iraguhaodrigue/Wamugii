import { Link } from 'react-router-dom'
import { ArrowRight, Layers } from 'lucide-react'
import type { Service } from '@/api/services'
import { Badge } from '@/components/ui'
import { formatMoney } from '@/utils/format'
import { paths } from '@/routes/paths'

export function ServiceCard({ service }: { service: Service }) {
  const price = formatMoney(service.price_from)

  return (
    <Link
      to={paths.serviceDetail(service.id)}
      className="group relative flex h-full flex-col rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm transition-all hover:-translate-y-0.5 hover:border-brand-400/40 hover:shadow-[var(--shadow-glow-brand)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
    >
      <div className="flex size-11 items-center justify-center rounded-lg bg-brand-50 text-brand-600">
        <Layers className="size-5" aria-hidden="true" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-slate-900">{service.name}</h3>
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
