import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { MessageCircle, Send, X } from 'lucide-react'
import { listServices } from '@/api/services'
import { listHostingPlans } from '@/api/hosting'
import { getPublicSettings } from '@/api/settings'
import { paths } from '@/routes/paths'
import { formatMoney } from '@/utils/format'
import { cn } from '@/utils/cn'

type TopicId = 'services' | 'hosting' | 'quote' | 'contact' | 'domains'

interface ChatEntry {
  id: number
  from: 'bot' | 'user'
  text: string
  /** Rendered as a bulleted list under the text. */
  bullets?: string[]
  /** An in-app link rendered as a button under the message. */
  action?: { label: string; to: string }
}

const QUICK_REPLIES: { id: TopicId; label: string }[] = [
  { id: 'services', label: 'What services do you offer?' },
  { id: 'hosting', label: 'How much does hosting cost?' },
  { id: 'quote', label: 'How do I request a quote?' },
  { id: 'domains', label: 'Do you offer domain registration?' },
  { id: 'contact', label: "What's your contact info?" },
]

const GREETING = "Hi! I'm here to help. What would you like to know?"

/**
 * A rule-based helper on the public site.
 *
 * Deliberately not an AI assistant: every answer is either fixed copy or built
 * from the public API the site already calls (services, hosting plans, company
 * settings), so it costs nothing per message and can never state a price or a
 * service that isn't real. Anything it doesn't recognise falls through to a
 * handoff rather than a guess.
 *
 * Mounted from PublicLayout only, so it never appears inside the authenticated
 * dashboards.
 */
export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [entries, setEntries] = useState<ChatEntry[]>([
    { id: 0, from: 'bot', text: GREETING },
  ])
  const nextId = useRef(1)
  const scrollRef = useRef<HTMLDivElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  // Nothing is fetched until the widget is actually opened, so a visitor who
  // never touches it pays no request cost.
  const { data: services } = useQuery({
    queryKey: ['services', 'list'],
    queryFn: () => listServices(),
    enabled: isOpen,
  })
  const { data: plans } = useQuery({
    queryKey: ['hosting', 'plans', 'public'],
    queryFn: () => listHostingPlans(),
    enabled: isOpen,
  })
  const { data: settings } = useQuery({
    queryKey: ['settings', 'public'],
    queryFn: getPublicSettings,
    enabled: isOpen,
  })

  const contactEmail = settings?.email ?? null

  function push(entry: Omit<ChatEntry, 'id'>) {
    setEntries((current) => [...current, { ...entry, id: nextId.current++ }])
  }

  function answer(topic: TopicId) {
    switch (topic) {
      case 'services': {
        if (!services || services.length === 0) {
          push({
            from: 'bot',
            text: "I couldn't load our services just now — the Services page has the full list.",
            action: { label: 'View Services', to: paths.services },
          })
          return
        }
        push({
          from: 'bot',
          text: 'Here’s what we do:',
          bullets: services.map((s) => s.name),
          action: { label: 'View Services', to: paths.services },
        })
        return
      }
      case 'hosting': {
        if (!plans || plans.length === 0) {
          push({
            from: 'bot',
            text: "I couldn't load our hosting plans just now — the Hosting page has current pricing.",
            action: { label: 'View Hosting', to: paths.hosting },
          })
          return
        }
        push({
          from: 'bot',
          text: 'Our hosting plans:',
          bullets: plans.map(
            (p) => `${p.name} — ${formatMoney(p.monthly_price)}/month or ${formatMoney(p.yearly_price)}/year`,
          ),
          action: { label: 'See full plans', to: paths.hosting },
        })
        return
      }
      case 'quote': {
        push({
          from: 'bot',
          text:
            "Fill in the Request a Quote form with what you need — no account required. " +
            "We'll review it and get back to you with a plan and a price.",
          action: { label: 'Request a Quote', to: paths.requestQuote },
        })
        return
      }
      case 'domains': {
        push({
          from: 'bot',
          text:
            'Yes — we can register and manage your domain for you, and point it at your ' +
            'hosting so you don’t have to deal with DNS. Tell us the domain you want in a ' +
            'quote request and we’ll take it from there.',
          action: { label: 'Request a Quote', to: paths.requestQuote },
        })
        return
      }
      case 'contact': {
        const bullets: string[] = []
        if (settings?.email) bullets.push(`Email: ${settings.email}`)
        if (settings?.phone) bullets.push(`Phone: ${settings.phone}`)
        if (settings?.address) bullets.push(settings.address)

        if (bullets.length === 0) {
          push({
            from: 'bot',
            text: "Our contact details aren't loading right now — the quote form is the surest way to reach us.",
            action: { label: 'Request a Quote', to: paths.requestQuote },
          })
          return
        }
        push({ from: 'bot', text: 'You can reach us here:', bullets })
        return
      }
    }
  }

  function handleQuickReply(topic: TopicId, label: string) {
    push({ from: 'user', text: label })
    answer(topic)
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text) return
    setDraft('')
    push({ from: 'user', text })
    // No matching intent: hand off rather than guess at an answer.
    push({
      from: 'bot',
      text: contactEmail
        ? `I'm not able to answer that directly yet — please use our Request a Quote form or contact us at ${contactEmail}.`
        : "I'm not able to answer that directly yet — please use our Request a Quote form and we'll get back to you.",
      action: { label: 'Request a Quote', to: paths.requestQuote },
    })
  }

  // Keep the newest message in view as the thread grows.
  useEffect(() => {
    if (isOpen) scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight })
  }, [entries, isOpen])

  // Escape closes, matching the notification dropdown.
  useEffect(() => {
    if (!isOpen) return
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsOpen(false)
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])

  return (
    <div className="fixed bottom-4 right-4 z-40 print:hidden">
      {isOpen && (
        <div
          ref={panelRef}
          role="dialog"
          aria-label="Chat with WAMUGII"
          className="mb-3 flex h-[28rem] w-[min(22rem,calc(100vw-2rem))] flex-col overflow-hidden rounded-xl border border-slate-200 bg-panel shadow-[var(--shadow-glow-brand)] backdrop-blur-xl"
        >
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">WAMUGII Help</p>
              <p className="text-xs text-slate-500">Quick answers about our services</p>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
              className="rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900"
            >
              <X className="size-4" aria-hidden="true" />
            </button>
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
            {entries.map((entry) => (
              <div
                key={entry.id}
                className={cn('flex', entry.from === 'user' ? 'justify-end' : 'justify-start')}
              >
                <div
                  className={cn(
                    'max-w-[85%] rounded-xl px-3 py-2 text-sm',
                    entry.from === 'user'
                      ? 'bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white'
                      : 'border border-slate-200 bg-slate-50 text-slate-700',
                  )}
                >
                  <p className="whitespace-pre-line">{entry.text}</p>
                  {entry.bullets && entry.bullets.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {entry.bullets.map((bullet) => (
                        <li key={bullet} className="flex gap-1.5 text-xs">
                          <span className="text-brand-400" aria-hidden="true">
                            •
                          </span>
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                  {entry.action && (
                    <Link
                      to={entry.action.to}
                      onClick={() => setIsOpen(false)}
                      className="mt-2 inline-flex items-center rounded-lg bg-brand-500/15 px-2.5 py-1 text-xs font-semibold text-brand-600 ring-1 ring-inset ring-brand-400/20 transition-colors hover:bg-brand-500/25"
                    >
                      {entry.action.label}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-slate-200 px-3 py-2">
            <div className="flex flex-wrap gap-1.5 pb-2">
              {QUICK_REPLIES.map((reply) => (
                <button
                  key={reply.id}
                  type="button"
                  onClick={() => handleQuickReply(reply.id, reply.label)}
                  className="rounded-full border border-slate-200 px-2.5 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-400/40 hover:text-brand-600"
                >
                  {reply.label}
                </button>
              ))}
            </div>
            <form onSubmit={handleSubmit} className="flex items-center gap-2">
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Type a message…"
                aria-label="Type a message"
                className="h-9 w-full rounded-lg border border-slate-300 bg-panel px-3 text-sm text-slate-900 placeholder:text-slate-400 focus-visible:border-brand-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              />
              <button
                type="submit"
                disabled={!draft.trim()}
                aria-label="Send message"
                className="inline-flex size-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white transition-[filter] hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Send className="size-4" aria-hidden="true" />
              </button>
            </form>
          </div>
        </div>
      )}

      <button
        type="button"
        onClick={() => setIsOpen((open) => !open)}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
        aria-expanded={isOpen}
        className="ml-auto flex size-12 items-center justify-center rounded-full bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
      >
        {isOpen ? (
          <X className="size-5" aria-hidden="true" />
        ) : (
          <MessageCircle className="size-5" aria-hidden="true" />
        )}
      </button>
    </div>
  )
}
