import { Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  className?: string
}

const sizeClasses = {
  sm: 'size-4',
  md: 'size-6',
  lg: 'size-10',
}

export function LoadingSpinner({ size = 'md', label = 'Loading', className }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex items-center justify-center', className)} role="status">
      <Loader2 className={cn('animate-spin text-brand-600', sizeClasses[size])} aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </div>
  )
}
