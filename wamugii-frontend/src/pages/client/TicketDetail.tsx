import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, SearchX, Send } from 'lucide-react'
import {
  addClientMessage,
  getClientTicket,
  type ClientTicket,
  type ClientTicketMessage,
} from '@/api/support'
import { useAuth } from '@/context/AuthContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, EmptyState, ErrorState, Skeleton, Textarea } from '@/components/ui'
import { TicketThread } from '@/components/support/TicketThread'
import { formatDateTime, formatEnumLabel } from '@/utils/format'
import { ticketPriorityVariant, ticketStatusVariant } from '@/utils/statusBadge'

/**
 * Read-and-reply client view. The payload comes from /client/tickets/{id},
 * which the backend scopes to the signed-in client and which has already had
 * internal notes stripped — there is nothing to filter out here.
 */
export function ClientTicketDetail() {
  const { ticketId } = useParams<{ ticketId: string }>()
  const queryClient = useQueryClient()
  const { user } = useAuth()

  const [reply, setReply] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  const ticketQuery = useQuery<ClientTicket, ApiError>({
    queryKey: ['client', 'tickets', 'detail', ticketId],
    queryFn: () => getClientTicket(ticketId!),
    enabled: Boolean(ticketId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const replyMutation = useMutation<ClientTicketMessage, ApiError, string>({
    mutationFn: (message) => addClientMessage(ticketId!, message),
    onSuccess: () => {
      // A reply can also flip WAITING_ON_CLIENT back to OPEN server-side, so
      // refetch the ticket rather than just appending the message.
      queryClient.invalidateQueries({ queryKey: ['client', 'tickets'] })
      setReply('')
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
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
        description="This ticket doesn't exist or isn't on your account."
        action={
          <Link
            to={paths.client.tickets}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Support
          </Link>
        }
      />
    )
  }

  if (ticketQuery.isError || !ticketQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this ticket"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => ticketQuery.refetch()}
      />
    )
  }

  const ticket = ticketQuery.data
  const isFinished = ticket.status === 'RESOLVED' || ticket.status === 'CLOSED'

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.client.tickets}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Support
        </Link>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{ticket.subject}</h1>
          <Badge variant={ticketStatusVariant[ticket.status]}>
            {formatEnumLabel(ticket.status)}
          </Badge>
        </div>
        <p className="mt-1 text-sm text-slate-500">
          Ticket #{ticket.id} · opened {formatDateTime(ticket.created_at)}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <TicketThread
            description={ticket.description}
            openedAt={ticket.created_at}
            openedByLabel="You"
            openedByViewer
            messages={ticket.messages}
            senderLabel={(senderId) => (senderId === user?.id ? 'You' : 'WAMUGII Support')}
            isOwn={(senderId) => senderId === user?.id}
          />

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Reply</h2>
            {ticket.status === 'WAITING_ON_CLIENT' && (
              <p className="mt-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                We&apos;re waiting on you — replying here puts this back with our team.
              </p>
            )}
            {isFinished && (
              <p className="mt-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
                This ticket is {formatEnumLabel(ticket.status).toLowerCase()}. You can still reply
                and we&apos;ll see it, but for something new please open a fresh ticket.
              </p>
            )}
            <form
              className="mt-4 space-y-3"
              onSubmit={(e) => {
                e.preventDefault()
                const trimmed = reply.trim()
                if (!trimmed) {
                  setFormError('Write a reply first.')
                  return
                }
                replyMutation.mutate(trimmed)
              }}
            >
              <Textarea
                label="Your message"
                rows={4}
                placeholder="Add anything else we should know…"
                value={reply}
                onChange={(e) => setReply(e.target.value)}
              />
              {formError && (
                <p role="alert" className="text-sm text-red-700">
                  {formError}
                </p>
              )}
              <div className="flex justify-end">
                <Button
                  type="submit"
                  size="sm"
                  leftIcon={<Send className="size-4" />}
                  isLoading={replyMutation.isPending}
                >
                  Send Reply
                </Button>
              </div>
            </form>
          </div>
        </div>

        <aside className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Details</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Category</dt>
              <dd className="font-medium text-slate-900">{formatEnumLabel(ticket.category)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Priority</dt>
              <dd>
                <Badge variant={ticketPriorityVariant[ticket.priority]}>
                  {formatEnumLabel(ticket.priority)}
                </Badge>
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Last update</dt>
              <dd className="font-medium text-slate-900">{formatDateTime(ticket.updated_at)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Related project</dt>
              <dd className="font-medium text-slate-900">
                {ticket.project_id ? (
                  <Link
                    to={paths.client.projectDetail(ticket.project_id)}
                    className="text-brand-600 hover:text-brand-700"
                  >
                    View project
                  </Link>
                ) : (
                  'None'
                )}
              </dd>
            </div>
          </dl>
        </aside>
      </div>
    </div>
  )
}
