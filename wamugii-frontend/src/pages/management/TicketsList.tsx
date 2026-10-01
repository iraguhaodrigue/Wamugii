import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, LifeBuoy, Plus, Search } from 'lucide-react'
import {
  TICKET_CATEGORIES,
  TICKET_PRIORITIES,
  TICKET_STATUSES,
  listTickets,
  type TicketCategory,
  type TicketPriority,
  type TicketStatus,
} from '@/api/support'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Input,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { StaffCreateTicketModal } from '@/components/support/StaffCreateTicketModal'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { ticketPriorityVariant, ticketStatusVariant } from '@/utils/statusBadge'
import { cn } from '@/utils/cn'

const LIMIT = 10

export function TicketsList() {
  usePageTitle('Support Tickets')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.ticketDetail : paths.staff.ticketDetail

  const { usersMap, users } = useUsersMap()

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<TicketStatus | ''>('')
  const [priority, setPriority] = useState<TicketPriority | ''>('')
  const [category, setCategory] = useState<TicketCategory | ''>('')
  const [assignee, setAssignee] = useState('')
  const [page, setPage] = useState(0)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status, priority, category, assignee])

  const {
    data: tickets,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['tickets', { status, priority, category, assignee, search: debouncedSearch, page }],
    queryFn: () =>
      listTickets({
        status: status || undefined,
        priority: priority || undefined,
        category: category || undefined,
        assigned_to: assignee ? Number(assignee) : undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || priority || category || assignee || debouncedSearch)
  const hasNextPage = (tickets?.length ?? 0) === LIMIT

  const assigneeOptions = [
    { value: '', label: 'Anyone' },
    ...users
      .filter((u) => u.role === 'STAFF' || u.role === 'ADMIN')
      .map((u) => ({ value: String(u.id), label: u.full_name })),
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Client tickets. Replies email the client; internal notes stay with us.
        </p>
        <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
          Raise Ticket
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div className="relative lg:col-span-3">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
            aria-hidden="true"
          />
          <Input
            type="search"
            placeholder="Search subject or description…"
            aria-label="Search tickets"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by status"
          options={[
            { value: '', label: 'All statuses' },
            ...TICKET_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
          ]}
          value={status}
          onChange={(e) => setStatus(e.target.value as TicketStatus | '')}
        />
        <Select
          aria-label="Filter by priority"
          options={[
            { value: '', label: 'All priorities' },
            ...TICKET_PRIORITIES.map((p) => ({ value: p, label: formatEnumLabel(p) })),
          ]}
          value={priority}
          onChange={(e) => setPriority(e.target.value as TicketPriority | '')}
        />
        <Select
          aria-label="Filter by category"
          options={[
            { value: '', label: 'All categories' },
            ...TICKET_CATEGORIES.map((c) => ({ value: c, label: formatEnumLabel(c) })),
          ]}
          value={category}
          onChange={(e) => setCategory(e.target.value as TicketCategory | '')}
        />
        <Select
          aria-label="Filter by assignee"
          options={assigneeOptions}
          value={assignee}
          onChange={(e) => setAssignee(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load tickets"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !tickets || tickets.length === 0 ? (
        <EmptyState
          icon={LifeBuoy}
          title={hasFilters ? 'No tickets match your filters' : 'No tickets yet'}
          description={
            hasFilters
              ? 'Try a different search or filter.'
              : 'Tickets clients open will show up here.'
          }
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Subject</TableHeaderCell>
              <TableHeaderCell>Client</TableHeaderCell>
              <TableHeaderCell>Category</TableHeaderCell>
              <TableHeaderCell>Priority</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Assigned</TableHeaderCell>
              <TableHeaderCell>Updated</TableHeaderCell>
            </TableHead>
            <TableBody>
              {tickets.map((ticket) => (
                <TableRow key={ticket.id} clickable onClick={() => navigate(detailPath(ticket.id))}>
                  <TableCell className="font-medium text-slate-900">{ticket.subject}</TableCell>
                  <TableCell>
                    {usersMap.get(ticket.client_id)?.full_name ?? `#${ticket.client_id}`}
                  </TableCell>
                  <TableCell>{formatEnumLabel(ticket.category)}</TableCell>
                  <TableCell>
                    <Badge variant={ticketPriorityVariant[ticket.priority]}>
                      {formatEnumLabel(ticket.priority)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={ticketStatusVariant[ticket.status]}>
                      {formatEnumLabel(ticket.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {ticket.assigned_to
                      ? (usersMap.get(ticket.assigned_to)?.full_name ?? `#${ticket.assigned_to}`)
                      : 'Unassigned'}
                  </TableCell>
                  <TableCell>{formatDate(ticket.updated_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isLoading && !isError && (tickets?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
        <div className="flex items-center justify-between border-t border-slate-200 pt-4">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="size-4" aria-hidden="true" />
            Previous
          </button>
          <span className="text-sm text-slate-500">Page {page + 1}</span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNextPage}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
            <ChevronRight className="size-4" aria-hidden="true" />
          </button>
        </div>
      )}

      <StaffCreateTicketModal
        key={isCreateOpen ? 'open' : 'closed'}
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        clients={users}
        onCreated={(ticket) => {
          setIsCreateOpen(false)
          navigate(detailPath(ticket.id))
        }}
      />
    </div>
  )
}
