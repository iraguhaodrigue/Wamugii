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
  success: 'bg-emerald-50 text-emerald-600',
  warning: 'bg-amber-50 text-amber-600',
}

export function StatCard({ icon: Icon, label, value, accent = 'brand', className }: StatCardProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md',
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
