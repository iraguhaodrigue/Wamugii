import { Skeleton } from '@/components/ui'

export function ServiceCardSkeleton() {
  return (
    <div className="flex h-full flex-col rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)]">
      <Skeleton className="size-11 rounded-lg" />
      <Skeleton className="mt-4 h-5 w-3/4" />
      <Skeleton className="mt-2 h-4 w-full" />
      <Skeleton className="mt-1.5 h-4 w-2/3" />
      <div className="mt-auto flex items-center justify-between pt-5">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-16" />
      </div>
    </div>
  )
}
