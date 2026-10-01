import { Lock, MessageSquare } from 'lucide-react'
import { formatDateTime } from '@/utils/format'
import { cn } from '@/utils/cn'

/**
 * The narrowest shape both thread payloads satisfy. `TicketMessageRead` (staff)
 * carries `is_internal_note`; `ClientTicketMessageRead` doesn't declare the
 * field at all — the backend strips internal notes before the client ever sees
 * the list, so an absent flag simply reads as "not a note".
 */
export interface ThreadMessage {
  id: number
  sender_id: number
  message: string
  created_at: string
  is_internal_note?: boolean
}

export interface TicketThreadProps {
  /** The ticket's opening description, rendered as the first bubble. */
  description: string
  openedAt: string
  /** Who opened it, as it should read to this viewer ("You", a client's name…). */
  openedByLabel: string
  /** Whether the opening description should sit on the viewer's own side. */
  openedByViewer?: boolean
  messages: ThreadMessage[]
  /** Resolves a sender id to a display name for this viewer. */
  senderLabel: (senderId: number) => string
  /** Sender ids whose messages align right — normally just the signed-in user. */
  isOwn: (senderId: number) => boolean
}

function Bubble({
  label,
  timestamp,
  body,
  align,
  tone,
}: {
  label: string
  timestamp: string
  body: string
  align: 'left' | 'right'
  tone: 'own' | 'other' | 'internal'
}) {
  return (
    <li className={cn('flex flex-col gap-1', align === 'right' ? 'items-end' : 'items-start')}>
      <div className="flex items-center gap-1.5 px-1 text-xs text-slate-500">
        {tone === 'internal' && <Lock className="size-3" aria-hidden="true" />}
        <span className="font-medium text-slate-600">{label}</span>
        <span aria-hidden="true">·</span>
        <time dateTime={timestamp}>{formatDateTime(timestamp)}</time>
      </div>
      <div
        className={cn(
          'max-w-[85%] whitespace-pre-line rounded-xl border px-4 py-3 text-sm',
          tone === 'own' && 'border-brand-200 bg-brand-50 text-slate-900',
          tone === 'other' && 'border-slate-200 bg-slate-50 text-slate-900',
          // Amber stays a literal light tint in both themes (see index.css) —
          // the same callout treatment used elsewhere in the app.
          tone === 'internal' && 'border-amber-200 bg-amber-50 text-amber-800',
        )}
      >
        {tone === 'internal' && (
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-amber-700">
            Internal note — not visible to the client
          </p>
        )}
        {body}
      </div>
    </li>
  )
}

/** The conversation on a ticket: opening description first, then every reply. */
export function TicketThread({
  description,
  openedAt,
  openedByLabel,
  openedByViewer = false,
  messages,
  senderLabel,
  isOwn,
}: TicketThreadProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
      <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
        <MessageSquare className="size-4" aria-hidden="true" />
        Conversation
      </h2>

      <ul className="mt-5 space-y-5">
        <Bubble
          label={openedByLabel}
          timestamp={openedAt}
          body={description}
          align={openedByViewer ? 'right' : 'left'}
          tone={openedByViewer ? 'own' : 'other'}
        />
        {messages.map((entry) => {
          const own = isOwn(entry.sender_id)
          return (
            <Bubble
              key={entry.id}
              label={senderLabel(entry.sender_id)}
              timestamp={entry.created_at}
              body={entry.message}
              align={entry.is_internal_note ? 'left' : own ? 'right' : 'left'}
              tone={entry.is_internal_note ? 'internal' : own ? 'own' : 'other'}
            />
          )
        })}
      </ul>

      {messages.length === 0 && (
        <p className="mt-5 text-sm text-slate-500">No replies yet.</p>
      )}
    </div>
  )
}
