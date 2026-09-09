import type { LucideIcon } from 'lucide-react'
import { cn } from '@/utils/cn'

export type StatCardAccent = 'brand' | 'accent' | 'success' | 'warning'

export interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  accent?: StatCardAccent
  className?: string
}

const accentClasses: Record<StatCardAccent, string> = {
  brand: 'bg-brand-50 text-brand-600',
  accent: 'bg-accent-50 text-accent-600',
  success: 'bg-green-50 text-green-600',
  warning: 'bg-amber-50 text-amber-600',
}

const glowClasses: Record<StatCardAccent, string> = {
  brand: 'hover:shadow-[var(--shadow-glow-brand)]',
  accent: 'hover:shadow-[var(--shadow-glow-accent)]',
  success: 'hover:shadow-[var(--shadow-card)]',
  warning: 'hover:shadow-[var(--shadow-card)]',
}

export function StatCard({ icon: Icon, label, value, accent = 'brand', className }: StatCardProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-4 rounded-xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] transition-shadow',
        glowClasses[accent],
        className,
      )}
    >
      <div className={cn('flex size-11 shrink-0 items-center justify-center rounded-lg', accentClasses[accent])}>
        <Icon className="size-5" aria-hidden="true" />
      </div>
      <div className="min-w-0">
        <p className="text-2xl font-semibold tracking-tight text-slate-900">{value}</p>
        <p className="truncate text-sm text-slate-500">{label}</p>
      </div>
    </div>
  )
}
