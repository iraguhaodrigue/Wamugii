import { getInitials } from '@/utils/format'
import { cn } from '@/utils/cn'

export interface AvatarProps {
  name: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'size-8 text-xs',
  md: 'size-10 text-sm',
  lg: 'size-12 text-base',
}

export function Avatar({ name, size = 'md', className }: AvatarProps) {
  return (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center rounded-full bg-brand-600 font-semibold text-white',
        sizeClasses[size],
        className,
      )}
      aria-hidden="true"
    >
      {getInitials(name)}
    </div>
  )
}
