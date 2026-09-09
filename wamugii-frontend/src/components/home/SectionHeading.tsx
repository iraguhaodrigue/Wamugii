import { cn } from '@/utils/cn'
import { Reveal } from '@/components/common/Reveal'

export interface SectionHeadingProps {
  label?: string
  title: string
  description?: string
  align?: 'center' | 'left'
  className?: string
}

/**
 * The one heading treatment every homepage section uses — label, title,
 * supporting line. Centralised so section rhythm stays consistent and the
 * type scale is defined in exactly one place.
 */
export function SectionHeading({ label, title, description, align = 'center', className }: SectionHeadingProps) {
  return (
    <Reveal className={cn(align === 'center' && 'mx-auto max-w-2xl text-center', 'max-w-2xl', className)}>
      {label && <span className="text-sm font-semibold uppercase tracking-wide text-brand-400">{label}</span>}
      <h2 className={cn('text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl', label && 'mt-3')}>{title}</h2>
      {description && <p className="mt-3 text-base text-slate-500">{description}</p>}
    </Reveal>
  )
}
