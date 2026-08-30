import { AlertTriangle } from 'lucide-react'
import { cn } from '@/utils/cn'
import { Button } from './Button'

export interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export function ErrorState({
  title = 'Something went wrong',
  message = 'Please try again. If the problem continues, contact support.',
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className={cn(
        'flex flex-col items-center justify-center gap-3 rounded-xl border border-red-200 bg-red-50 px-6 py-12 text-center',
        className,
      )}
    >
      <AlertTriangle className="size-10 text-red-500" aria-hidden="true" />
      <div className="space-y-1">
        <p className="text-sm font-medium text-red-900">{title}</p>
        <p className="text-sm text-red-700">{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  )
}
