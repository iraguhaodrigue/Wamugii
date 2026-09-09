import { Sparkles } from 'lucide-react'

const areas = ['Web', 'Software', 'IT Consultancy', 'Hosting', 'Support']

/**
 * Slim strip above the floating nav. Content is limited to what the business
 * verifiably does (the service areas actually in the catalogue) — no offers,
 * counts or claims.
 */
export function AnnouncementBar() {
  return (
    <div className="relative z-40 border-b border-white/5 bg-black/40 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-center gap-2 px-4 py-2 text-center">
        <Sparkles className="hidden size-3 shrink-0 text-brand-400 sm:block" aria-hidden="true" />
        <p className="text-[11px] font-medium tracking-wide text-slate-400 sm:text-xs">
          <span className="text-slate-900">WAMUGII TECH SOLUTIONS</span>
          <span className="mx-2 text-slate-500" aria-hidden="true">
            —
          </span>
          <span className="hidden sm:inline">Digital solutions for growing businesses </span>
          <span className="text-slate-500">{areas.join(' • ')}</span>
        </p>
      </div>
    </div>
  )
}
