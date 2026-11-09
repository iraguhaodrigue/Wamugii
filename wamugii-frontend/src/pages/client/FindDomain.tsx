import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { DomainSearch } from '@/components/domains/DomainSearch'
import { paths } from '@/routes/paths'

/** Search for a domain and request it, inside the client portal. */
export function ClientFindDomain() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <Link to={paths.client.domains} className="inline-flex items-center gap-1.5 text-sm text-slate-600 hover:text-slate-900">
        <ArrowLeft className="size-4" aria-hidden="true" /> My Domains
      </Link>
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Find a domain</h1>
        <p className="mt-1 text-sm text-slate-600">
          Check which names are free and request one. We register it for you and send the invoice.
        </p>
      </div>
      <DomainSearch mode="client" />
    </div>
  )
}
