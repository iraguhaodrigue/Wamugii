import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/utils/cn'

export type CardGlow = 'none' | 'brand' | 'accent'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string
  description?: string
  footer?: ReactNode
  /** Selective glow for hierarchy — use sparingly, not on every card. */
  glow?: CardGlow
}

const glowClasses: Record<CardGlow, string> = {
  none: 'shadow-[var(--shadow-card)]',
  brand: 'shadow-[var(--shadow-glow-brand)]',
  accent: 'shadow-[var(--shadow-glow-accent)]',
}

export function Card({ className, title, description, footer, glow = 'none', children, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-panel backdrop-blur-sm',
        glowClasses[glow],
        className,
      )}
      {...props}
    >
      {(title || description) && (
        <div className="border-b border-slate-200 px-5 py-4">
          {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
          {description && <p className="mt-1 text-sm text-slate-500">{description}</p>}
        </div>
      )}
      <div className="px-5 py-4">{children}</div>
      {footer && <div className="border-t border-slate-200 px-5 py-4">{footer}</div>}
    </div>
  )
}
