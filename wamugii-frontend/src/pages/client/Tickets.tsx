import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { LifeBuoy, Plus } from 'lucide-react'
import { TICKET_STATUSES, listClientTickets, type TicketStatus } from '@/api/support'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { ClientCreateTicketModal } from '@/components/support/ClientCreateTicketModal'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { ticketStatusVariant } from '@/utils/statusBadge'

/** The client's own support tickets, newest first. */
export function ClientTickets() {
  const navigate = useNavigate()
  const [status, setStatus] = useState<TicketStatus | ''>('')
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  const {
    data: tickets,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['client', 'tickets', { status }],
    queryFn: () => listClientTickets({ status: status || undefined, limit: 50 }),
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Support</h1>
          <p className="mt-1 text-sm text-slate-500">
            Open a ticket and our team will reply here — you&apos;ll get an email when we do.
          </p>
        </div>
        <Button
          size="sm"
          className="shrink-0"
          leftIcon={<Plus className="size-4" />}
          onClick={() => setIsCreateOpen(true)}
        >
          New Ticket
        </Button>
      </div>

      <div className="sm:max-w-xs">
        <Select
          aria-label="Filter by status"
          options={[
            { value: '', label: 'All statuses' },
            ...TICKET_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
          ]}
          value={status}
          onChange={(e) => setStatus(e.target.value as TicketStatus | '')}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load your tickets"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !tickets || tickets.length === 0 ? (
        <EmptyState
          icon={LifeBuoy}
          title={status ? 'No tickets with that status' : 'No tickets yet'}
          description={
            status
              ? 'Try a different status filter.'
              : 'Need a hand with something? Open a ticket and we’ll pick it up.'
          }
          action={
            !status ? (
              <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
                New Ticket
              </Button>
            ) : undefined
          }
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Subject</TableHeaderCell>
            <TableHeaderCell>Category</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Opened</TableHeaderCell>
            <TableHeaderCell>Last update</TableHeaderCell>
          </TableHead>
          <TableBody>
            {tickets.map((ticket) => (
              <TableRow
                key={ticket.id}
                clickable
                onClick={() => navigate(paths.client.ticketDetail(ticket.id))}
              >
                <TableCell className="font-medium text-slate-900">{ticket.subject}</TableCell>
                <TableCell>{formatEnumLabel(ticket.category)}</TableCell>
                <TableCell>
                  <Badge variant={ticketStatusVariant[ticket.status]}>
                    {formatEnumLabel(ticket.status)}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(ticket.created_at)}</TableCell>
                <TableCell>{formatDate(ticket.updated_at)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <ClientCreateTicketModal
        key={isCreateOpen ? 'open' : 'closed'}
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreated={(ticket) => {
          setIsCreateOpen(false)
          navigate(paths.client.ticketDetail(ticket.id))
        }}
      />
    </div>
  )
}
