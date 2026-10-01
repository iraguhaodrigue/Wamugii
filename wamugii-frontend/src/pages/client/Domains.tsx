import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, Globe } from 'lucide-react'
import { listClientDomains } from '@/api/domains'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { domainStatusVariant } from '@/utils/statusBadge'

/** Read-only view of the signed-in client's own domains. */
export function ClientDomains() {
  const navigate = useNavigate()
  const {
    data: domains,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['client', 'domains'], queryFn: listClientDomains })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Domains</h1>
          <p className="mt-1 text-sm text-slate-500">
            Domains we manage for you, with their status and renewal dates.
          </p>
        </div>
        <Link
          to={`${paths.requestQuote}?service=domain`}
          className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
        >
          Register another
          <ArrowRight className="size-4" aria-hidden="true" />
        </Link>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load your domains"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !domains || domains.length === 0 ? (
        <EmptyState
          icon={Globe}
          title="No domains yet"
          description="Any domain we register for you will show up here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Domain</TableHeaderCell>
            <TableHeaderCell>Registrar</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Registered</TableHeaderCell>
            <TableHeaderCell>Expires</TableHeaderCell>
          </TableHead>
          <TableBody>
            {domains.map((domain) => (
              <TableRow
                key={domain.id}
                clickable
                onClick={() => navigate(paths.client.domainDetail(domain.id))}
              >
                <TableCell className="font-medium text-slate-900">{domain.domain_name}</TableCell>
                <TableCell>{domain.registrar}</TableCell>
                <TableCell>
                  <Badge variant={domainStatusVariant[domain.status]}>
                    {formatEnumLabel(domain.status)}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(domain.registered_date)}</TableCell>
                <TableCell>{formatDate(domain.expires_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <p className="text-xs text-slate-500">
        Renewals are handled by our team — we&apos;ll be in touch before a domain expires.
      </p>
    </div>
  )
}
