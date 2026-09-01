import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, FolderKanban, Search } from 'lucide-react'
import { listClientProjects, type ProjectStatus } from '@/api/clientPortal'
import { EmptyState, ErrorState, Input, Select, Skeleton } from '@/components/ui'
import { ClientProjectRow } from '@/components/projects/ClientProjectRow'
import { formatEnumLabel } from '@/utils/format'
import { cn } from '@/utils/cn'

const LIMIT = 10

const PROJECT_STATUSES: ProjectStatus[] = [
  'PENDING',
  'PLANNING',
  'IN_PROGRESS',
  'ON_HOLD',
  'TESTING',
  'CLIENT_REVIEW',
  'COMPLETED',
  'CANCELLED',
]

const statusOptions = [
  { value: '', label: 'All statuses' },
  ...PROJECT_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) })),
]

export function ClientProjects() {
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<ProjectStatus | ''>('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status])

  const {
    data: projects,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['client', 'projects', { status, search: debouncedSearch, page }],
    queryFn: () =>
      listClientProjects({
        status: status || undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || debouncedSearch)
  const hasNextPage = (projects?.length ?? 0) === LIMIT

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Projects</h1>
        <p className="mt-1 text-sm text-slate-500">Track the status and progress of every project you have with us.</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search by project title…"
            aria-label="Search projects"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select
          aria-label="Filter by status"
          options={statusOptions}
          value={status}
          onChange={(e) => setStatus(e.target.value as ProjectStatus | '')}
          className="sm:w-56"
        />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load your projects"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !projects || projects.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title={hasFilters ? 'No projects match your filters' : "You don't have any projects yet"}
          description={hasFilters ? 'Try a different search or status.' : 'Once a project is set up for you, it will show up here.'}
        />
      ) : (
        <div className={cn('space-y-3 transition-opacity', isFetching && 'opacity-60')}>
          {projects.map((project) => (
            <ClientProjectRow key={project.id} project={project} />
          ))}
        </div>
      )}

      {!isLoading && !isError && (projects?.length ?? 0) > 0 && (page > 0 || hasNextPage) && (
        <div className="flex items-center justify-between border-t border-slate-200 pt-4">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft className="size-4" aria-hidden="true" />
            Previous
          </button>
          <span className="text-sm text-slate-500">Page {page + 1}</span>
          <button
            type="button"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNextPage}
            className="inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
            <ChevronRight className="size-4" aria-hidden="true" />
          </button>
        </div>
      )}
    </div>
  )
}
