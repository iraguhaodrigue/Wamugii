import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowRight, Server } from 'lucide-react'
import { listClientHosting } from '@/api/hosting'
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
import { hostingStatusVariant } from '@/utils/statusBadge'

/** Read-only view of the signed-in client's own hosting. */
export function ClientHosting() {
  const {
    data: accounts,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['client', 'hosting'], queryFn: listClientHosting })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Hosting</h1>
          <p className="mt-1 text-sm text-slate-500">
            Your hosting plans, their status, and when they renew.
          </p>
        </div>
        <Link
          to={`${paths.requestQuote}?service=hosting`}
          className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
        >
          Renew / Upgrade
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
          title="Couldn't load your hosting"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !accounts || accounts.length === 0 ? (
        <EmptyState
          icon={Server}
          title="No hosting yet"
          description="Once we set up hosting for you, it'll show up here."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Domain</TableHeaderCell>
            <TableHeaderCell>Plan</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Billing</TableHeaderCell>
            <TableHeaderCell>Next billing</TableHeaderCell>
            <TableHeaderCell>Expires</TableHeaderCell>
          </TableHead>
          <TableBody>
            {accounts.map((account) => (
              <TableRow key={account.id}>
                <TableCell className="font-medium text-slate-900">
                  <Link
                    to={paths.client.hostingDetail(account.id)}
                    className="hover:text-brand-600"
                  >
                    {account.domain ?? `Hosting #${account.id}`}
                  </Link>
                </TableCell>
                <TableCell>{account.plan?.name ?? '—'}</TableCell>
                <TableCell>
                  <Badge variant={hostingStatusVariant[account.status]}>
                    {formatEnumLabel(account.status)}
                  </Badge>
                </TableCell>
                <TableCell>{formatEnumLabel(account.billing_cycle)}</TableCell>
                <TableCell>{formatDate(account.next_billing_date)}</TableCell>
                <TableCell>{formatDate(account.expires_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
