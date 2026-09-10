import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Bell, CheckCheck } from 'lucide-react'
import {
  getUnreadCount,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type NotificationRead,
} from '@/api/notifications'
import { useAuth } from '@/context/AuthContext'
import { paths } from '@/routes/paths'
import { LoadingSpinner } from '@/components/ui'
import { formatRelativeTime } from '@/utils/format'
import { cn } from '@/utils/cn'
import type { components } from '@/types/api'

type Role = components['schemas']['Role']

const RECENT_LIMIT = 10
/** Light touch — the badge is a nicety, not a live feed. */
const UNREAD_POLL_MS = 45_000

/**
 * Where a notification's related resource lives for each role.
 *
 * The same PROJECT_CREATED notification points at three different URLs
 * depending on who is reading it, so this is keyed by role first — a client
 * must never be sent to an /admin/* route they'd only be bounced out of.
 *
 * A missing entry is deliberate, not an oversight: clients have no quote
 * detail screen, so a client's quote notification is marked read and goes
 * nowhere. Unknown `related_type` values fall through the same path.
 */
const RESOURCE_ROUTES: Record<Role, Record<string, (id: number) => string>> = {
  ADMIN: {
    invoice: paths.admin.invoiceDetail,
    project: paths.admin.projectDetail,
    quote: paths.admin.quoteDetail,
  },
  STAFF: {
    invoice: paths.staff.invoiceDetail,
    project: paths.staff.projectDetail,
    quote: paths.staff.quoteDetail,
  },
  CLIENT: {
    invoice: paths.client.invoiceDetail,
    project: paths.client.projectDetail,
    // No client-facing quote detail route exists — see the note above.
  },
}

function resolveRoute(
  role: Role | undefined,
  notification: NotificationRead,
): string | null {
  if (!role || !notification.related_type || notification.related_id === null) return null
  const builder = RESOURCE_ROUTES[role]?.[notification.related_type]
  return builder ? builder(notification.related_id) : null
}

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAuth()

  const unreadQuery = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: getUnreadCount,
    refetchInterval: UNREAD_POLL_MS,
  })

  // The list is only fetched once the panel is actually opened, so a user who
  // never touches the bell costs one small count request per poll.
  const listQuery = useQuery({
    queryKey: ['notifications', 'recent'],
    queryFn: () => listNotifications({ limit: RECENT_LIMIT }),
    enabled: isOpen,
  })

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ['notifications'] })
  }

  const markReadMutation = useMutation({
    mutationFn: (id: number) => markNotificationRead(id),
    onSuccess: refresh,
  })

  const markAllMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: refresh,
  })

  // Close on outside click / Escape — a plain listener pair rather than
  // pulling in a popover library for one dropdown.
  useEffect(() => {
    if (!isOpen) return

    function handlePointerDown(event: MouseEvent) {
      if (!containerRef.current?.contains(event.target as Node)) setIsOpen(false)
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false)
    }

    document.addEventListener('mousedown', handlePointerDown)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handlePointerDown)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen])

  const unread = unreadQuery.data?.unread ?? 0
  const notifications = listQuery.data ?? []

  function handleSelect(notification: NotificationRead) {
    if (!notification.is_read) {
      markReadMutation.mutate(notification.id)
    }
    setIsOpen(false)

    const destination = resolveRoute(user?.role, notification)
    // No route for this resource/role pairing: it still gets marked read, it
    // just doesn't navigate anywhere.
    if (destination) navigate(destination)
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-label={unread > 0 ? `Notifications (${unread} unread)` : 'Notifications'}
        aria-expanded={isOpen}
        aria-haspopup="menu"
        className="relative inline-flex size-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900"
      >
        <Bell className="size-4" aria-hidden="true" />
        {unread > 0 && (
          <span className="absolute -right-0.5 -top-0.5 inline-flex min-w-4 items-center justify-center rounded-full bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-1 text-[10px] font-semibold leading-4 text-white">
            {unread > 9 ? '9+' : unread}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          role="menu"
          aria-label="Notifications"
          className="absolute right-0 z-30 mt-2 w-80 overflow-hidden rounded-xl border border-slate-200 bg-panel shadow-[var(--shadow-card)] backdrop-blur-xl sm:w-96"
        >
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <p className="text-sm font-semibold text-slate-900">Notifications</p>
            {unread > 0 && (
              <button
                type="button"
                onClick={() => markAllMutation.mutate()}
                disabled={markAllMutation.isPending}
                className="inline-flex items-center gap-1.5 text-xs font-medium text-brand-600 transition-colors hover:text-brand-700 disabled:opacity-50"
              >
                <CheckCheck className="size-3.5" aria-hidden="true" />
                Mark all as read
              </button>
            )}
          </div>

          <div className="max-h-96 overflow-y-auto">
            {listQuery.isLoading ? (
              <div className="py-10">
                <LoadingSpinner size="sm" label="Loading notifications" />
              </div>
            ) : listQuery.isError ? (
              <div className="px-4 py-8 text-center">
                <p className="text-sm text-slate-500">Couldn&apos;t load notifications.</p>
                <button
                  type="button"
                  onClick={() => listQuery.refetch()}
                  className="mt-2 text-xs font-medium text-brand-600 hover:text-brand-700"
                >
                  Try again
                </button>
              </div>
            ) : notifications.length === 0 ? (
              <div className="px-4 py-10 text-center">
                <Bell className="mx-auto size-8 text-slate-400" aria-hidden="true" />
                <p className="mt-2 text-sm font-medium text-slate-900">You&apos;re all caught up</p>
                <p className="mt-0.5 text-xs text-slate-500">
                  Updates on your projects and invoices will show up here.
                </p>
              </div>
            ) : (
              <ul className="divide-y divide-slate-100">
                {notifications.map((notification) => (
                  <li key={notification.id}>
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => handleSelect(notification)}
                      className={cn(
                        'flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-slate-100',
                        !notification.is_read && 'bg-brand-500/5',
                      )}
                    >
                      <span
                        className={cn(
                          'mt-1.5 size-2 shrink-0 rounded-full',
                          notification.is_read ? 'bg-transparent' : 'bg-brand-500',
                        )}
                        aria-hidden="true"
                      />
                      <span className="min-w-0 flex-1">
                        <span
                          className={cn(
                            'block truncate text-sm text-slate-900',
                            notification.is_read ? 'font-medium' : 'font-semibold',
                          )}
                        >
                          {notification.title}
                        </span>
                        <span className="mt-0.5 line-clamp-2 block text-xs text-slate-500">
                          {notification.message}
                        </span>
                        <span className="mt-1 block text-xs text-slate-400">
                          {formatRelativeTime(notification.created_at)}
                          {!notification.is_read && <span className="sr-only"> (unread)</span>}
                        </span>
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {notifications.length >= RECENT_LIMIT && (
            <p className="border-t border-slate-200 px-4 py-2.5 text-center text-xs text-slate-500">
              Showing your {RECENT_LIMIT} most recent
            </p>
          )}
        </div>
      )}
    </div>
  )
}
