import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Lock, SearchX, Send, Trash2 } from 'lucide-react'
import {
  NOTIFYING_TICKET_STATUSES,
  TICKET_CATEGORIES,
  TICKET_PRIORITIES,
  TICKET_STATUSES,
  addStaffMessage,
  deactivateTicket,
  getTicket,
  updateTicket,
  type SupportTicket,
  type SupportTicketUpdate,
  type TicketCategory,
  type TicketMessage,
  type TicketPriority,
  type TicketStatus,
} from '@/api/support'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  Select,
  Skeleton,
  Textarea,
} from '@/components/ui'
import { TicketThread } from '@/components/support/TicketThread'
import { formatDateTime, formatEnumLabel } from '@/utils/format'
import { ticketPriorityVariant, ticketStatusVariant } from '@/utils/statusBadge'

/** Copy for the confirm step on each status that emails the client. */
const STATUS_CONFIRM: Partial<Record<TicketStatus, { title: string; description: string }>> = {
  RESOLVED: {
    title: 'Mark this ticket resolved?',
    description: "The client is notified and emailed that we've resolved it.",
  },
  CLOSED: {
    title: 'Close this ticket?',
    description: 'The client is notified and emailed that the ticket is closed.',
  },
  WAITING_ON_CLIENT: {
    title: 'Put this back to the client?',
    description:
      "The client is notified and emailed that we're waiting on them. Their next reply reopens it.",
  },
}

export function TicketDetail() {
  const { ticketId } = useParams<{ ticketId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { usersMap, users } = useUsersMap()

  const [pendingStatus, setPendingStatus] = useState<TicketStatus | null>(null)
  const [reply, setReply] = useState('')
  const [isInternal, setIsInternal] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const ticketQuery = useQuery<SupportTicket, ApiError>({
    queryKey: ['tickets', 'detail', ticketId],
    queryFn: () => getTicket(ticketId!),
    enabled: Boolean(ticketId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const ticket = ticketQuery.data
  usePageTitle(ticket?.subject ?? 'Ticket')

  const listPath = isAdmin ? paths.admin.tickets : paths.staff.tickets

  const updateMutation = useMutation<SupportTicket, ApiError, SupportTicketUpdate>({
    mutationFn: (payload) => updateTicket(ticketId!, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['tickets', 'detail', ticketId], updated)
      queryClient.invalidateQueries({ queryKey: ['tickets'] })
      setPendingStatus(null)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const replyMutation = useMutation<TicketMessage, ApiError, { message: string; internal: boolean }>({
    mutationFn: ({ message, internal }) =>
      addStaffMessage(ticketId!, { message, is_internal_note: internal }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] })
      setReply('')
      setIsInternal(false)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: () => deactivateTicket(ticketId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] })
      navigate(listPath)
    },
  })

  if (ticketQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = ticketQuery.isError && ticketQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Ticket not found"
        description="This ticket doesn't exist."
        action={
          <Link
            to={listPath}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Support Tickets
          </Link>
        }
      />
    )
  }

  if (ticketQuery.isError || !ticket) {
    return (
      <ErrorState
        title="Couldn't load this ticket"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => ticketQuery.refetch()}
      />
    )
  }

  const client = usersMap.get(ticket.client_id)
  const staffOptions = [
    { value: '', label: 'Unassigned' },
    ...users
      .filter((u) => (u.role === 'STAFF' || u.role === 'ADMIN') && u.is_active)
      .map((u) => ({ value: String(u.id), label: u.full_name })),
  ]

  function applyStatus(next: TicketStatus) {
    // Each of these emails the client, so confirm before sending.
    if (NOTIFYING_TICKET_STATUSES.includes(next)) {
      setPendingStatus(next)
      return
    }
    updateMutation.mutate({ status: next })
  }

  const confirmCopy = pendingStatus ? STATUS_CONFIRM[pendingStatus] : undefined

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={listPath}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Support Tickets
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{ticket.subject}</h1>
            <Badge variant={ticketStatusVariant[ticket.status]}>
              {formatEnumLabel(ticket.status)}
            </Badge>
            <Badge variant={ticketPriorityVariant[ticket.priority]}>
              {formatEnumLabel(ticket.priority)}
            </Badge>
            {!ticket.is_active && <Badge variant="neutral">Deleted</Badge>}
          </div>
          {isAdmin && ticket.is_active && (
            <Button
              size="sm"
              variant="danger"
              leftIcon={<Trash2 className="size-4" />}
              onClick={() => setIsDeleteOpen(true)}
            >
              Delete
            </Button>
          )}
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Ticket #{ticket.id} · opened {formatDateTime(ticket.created_at)}
        </p>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <TicketThread
            description={ticket.description}
            openedAt={ticket.created_at}
            openedByLabel={client ? client.full_name : `Client #${ticket.client_id}`}
            messages={ticket.messages}
            senderLabel={(senderId) =>
              senderId === user?.id
                ? 'You'
                : (usersMap.get(senderId)?.full_name ?? `User #${senderId}`)
            }
            isOwn={(senderId) => senderId !== ticket.client_id}
          />

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Reply</h2>
            <form
              className="mt-4 space-y-3"
              onSubmit={(e) => {
                e.preventDefault()
                const trimmed = reply.trim()
                if (!trimmed) {
                  setFormError('Write a message first.')
                  return
                }
                replyMutation.mutate({ message: trimmed, internal: isInternal })
              }}
            >
              <Textarea
                label={isInternal ? 'Internal note' : 'Message to the client'}
                rows={4}
                placeholder={
                  isInternal
                    ? 'Context for the team — never sent to the client.'
                    : 'This is emailed to the client.'
                }
                value={reply}
                onChange={(e) => setReply(e.target.value)}
              />

              <label className="inline-flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-600">
                <input
                  type="checkbox"
                  className="size-4 rounded border-slate-300 accent-[var(--color-brand-solid)]"
                  checked={isInternal}
                  onChange={(e) => setIsInternal(e.target.checked)}
                />
                <Lock className="size-3.5 text-slate-400" aria-hidden="true" />
                Internal note (not visible to the client)
              </label>

              <p className="text-xs text-slate-500">
                {isInternal
                  ? 'Stays on the ticket for staff only — no notification, no email.'
                  : 'The client is notified and emailed this reply.'}
              </p>

              {formError && (
                <p role="alert" className="text-sm text-red-700">
                  {formError}
                </p>
              )}

              <div className="flex justify-end">
                <Button
                  type="submit"
                  size="sm"
                  variant={isInternal ? 'outline' : 'primary'}
                  leftIcon={isInternal ? <Lock className="size-4" /> : <Send className="size-4" />}
                  isLoading={replyMutation.isPending}
                >
                  {isInternal ? 'Save Internal Note' : 'Send Reply'}
                </Button>
              </div>
            </form>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Triage</h2>
            <Select
              label="Status"
              options={TICKET_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))}
              value={ticket.status}
              disabled={updateMutation.isPending}
              onChange={(e) => applyStatus(e.target.value as TicketStatus)}
              hint="Resolved, Closed and Waiting On Client email the client."
            />
            <Select
              label="Priority"
              options={TICKET_PRIORITIES.map((p) => ({ value: p, label: formatEnumLabel(p) }))}
              value={ticket.priority}
              disabled={updateMutation.isPending}
              onChange={(e) =>
                updateMutation.mutate({ priority: e.target.value as TicketPriority })
              }
            />
            <Select
              label="Category"
              options={TICKET_CATEGORIES.map((c) => ({ value: c, label: formatEnumLabel(c) }))}
              value={ticket.category}
              disabled={updateMutation.isPending}
              onChange={(e) =>
                updateMutation.mutate({ category: e.target.value as TicketCategory })
              }
            />
            <Select
              label="Assigned to"
              options={staffOptions}
              value={ticket.assigned_to ? String(ticket.assigned_to) : ''}
              disabled={updateMutation.isPending}
              onChange={(e) =>
                updateMutation.mutate({
                  assigned_to: e.target.value ? Number(e.target.value) : null,
                })
              }
              hint="Internal only — the client isn't told who's on it."
            />
          </div>

          <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Details
            </h2>
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Client</dt>
                <dd className="font-medium text-slate-900">
                  {client ? (
                    isAdmin ? (
                      <Link
                        to={paths.admin.userDetail(client.id)}
                        className="text-brand-600 hover:text-brand-700"
                      >
                        {client.full_name}
                      </Link>
                    ) : (
                      client.full_name
                    )
                  ) : (
                    `#${ticket.client_id}`
                  )}
                </dd>
              </div>
              {client && <div>
                <dt className="text-slate-500">Email</dt>
                <dd className="font-medium text-slate-900">{client.email}</dd>
              </div>}
              <div>
                <dt className="text-slate-500">Related project</dt>
                <dd className="font-medium text-slate-900">
                  {ticket.project_id ? (
                    <Link
                      to={
                        isAdmin
                          ? paths.admin.projectDetail(ticket.project_id)
                          : paths.staff.projectDetail(ticket.project_id)
                      }
                      className="text-brand-600 hover:text-brand-700"
                    >
                      View project
                    </Link>
                  ) : (
                    'None'
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Last update</dt>
                <dd className="font-medium text-slate-900">{formatDateTime(ticket.updated_at)}</dd>
              </div>
            </dl>
          </div>
        </aside>
      </div>

      <ConfirmDialog
        isOpen={pendingStatus !== null}
        onClose={() => setPendingStatus(null)}
        onConfirm={() => pendingStatus && updateMutation.mutate({ status: pendingStatus })}
        title={confirmCopy?.title ?? 'Change this ticket status?'}
        description={confirmCopy?.description ?? 'The client is notified and emailed.'}
        confirmLabel="Change status"
        isLoading={updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this ticket?"
        description="This deactivates the ticket. It disappears from the list and from the client's portal."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
