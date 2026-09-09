import { cn } from '@/utils/cn'

export interface ProgressBarProps {
  value: number
  className?: string
}

export function ProgressBar({ value, className }: ProgressBarProps) {
  const clamped = Math.min(100, Math.max(0, value))

  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(clamped)}
      aria-valuemin={0}
      aria-valuemax={100}
      className={cn('h-2 w-full overflow-hidden rounded-full bg-slate-100', className)}
    >
      <div
        className="h-full rounded-full bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] transition-[width]"
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
