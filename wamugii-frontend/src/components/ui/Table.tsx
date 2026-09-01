import type { HTMLAttributes, TdHTMLAttributes, ThHTMLAttributes } from 'react'
import { cn } from '@/utils/cn'

export function Table({ className, children, ...props }: HTMLAttributes<HTMLTableElement>) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-panel shadow-sm">
      <table className={cn('w-full min-w-[640px] divide-y divide-slate-200 text-sm', className)} {...props}>
        {children}
      </table>
    </div>
  )
}

export function TableHead({ className, children, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <thead className={cn('bg-slate-50', className)} {...props}>
      {children}
    </thead>
  )
}

export function TableHeaderCell({ className, children, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      scope="col"
      className={cn(
        'whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500',
        className,
      )}
      {...props}
    >
      {children}
    </th>
  )
}

export function TableBody({ className, children, ...props }: HTMLAttributes<HTMLTableSectionElement>) {
  return (
    <tbody className={cn('divide-y divide-slate-100 bg-panel', className)} {...props}>
      {children}
    </tbody>
  )
}

export interface TableRowProps extends HTMLAttributes<HTMLTableRowElement> {
  clickable?: boolean
}

export function TableRow({ className, clickable, children, ...props }: TableRowProps) {
  return (
    <tr
      className={cn('transition-colors', clickable && 'cursor-pointer hover:bg-brand-600/10', className)}
      {...props}
    >
      {children}
    </tr>
  )
}

export function TableCell({ className, children, ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return (
    <td className={cn('px-4 py-3 align-middle text-slate-700', className)} {...props}>
      {children}
    </td>
  )
}
