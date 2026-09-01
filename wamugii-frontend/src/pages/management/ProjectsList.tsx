import { useEffect, useState } from 'react'
import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, FolderKanban, Plus, Search } from 'lucide-react'
import { listProjects, type ProjectPriority, type ProjectStatus } from '@/api/projects'
import { listServices } from '@/api/services'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Input,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { CreateProjectModal } from '@/components/projects/CreateProjectModal'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'
import { projectPriorityVariant, projectStatusVariant } from '@/utils/statusBadge'
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
const PROJECT_PRIORITIES: ProjectPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']

export function ProjectsList() {
  usePageTitle('Projects')
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const detailPath = isAdmin ? paths.admin.projectDetail : paths.staff.projectDetail

  const { usersMap, users } = useUsersMap()
  const { data: services } = useQuery({ queryKey: ['services', 'filter'], queryFn: () => listServices() })

  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [status, setStatus] = useState<ProjectStatus | ''>('')
  const [priority, setPriority] = useState<ProjectPriority | ''>('')
  const [serviceId, setServiceId] = useState('')
  const [clientId, setClientId] = useState('')
  const [page, setPage] = useState(0)
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(search.trim()), 400)
    return () => clearTimeout(timeout)
  }, [search])

  useEffect(() => {
    setPage(0)
  }, [debouncedSearch, status, priority, serviceId, clientId])

  const {
    data: projects,
    isLoading,
    isError,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ['projects', { status, priority, serviceId, clientId, search: debouncedSearch, page }],
    queryFn: () =>
      listProjects({
        status: status || undefined,
        priority: priority || undefined,
        service_id: serviceId ? Number(serviceId) : undefined,
        client_id: clientId ? Number(clientId) : undefined,
        search: debouncedSearch || undefined,
        limit: LIMIT,
        offset: page * LIMIT,
      }),
    placeholderData: keepPreviousData,
  })

  const hasFilters = Boolean(status || priority || serviceId || clientId || debouncedSearch)
  const hasNextPage = (projects?.length ?? 0) === LIMIT

  const statusOptions = [{ value: '', label: 'All statuses' }, ...PROJECT_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))]
  const priorityOptions = [{ value: '', label: 'All priorities' }, ...PROJECT_PRIORITIES.map((p) => ({ value: p, label: formatEnumLabel(p) }))]
  const serviceOptions = [{ value: '', label: 'All services' }, ...(services?.map((s) => ({ value: String(s.id), label: s.name })) ?? [])]
  const clientOptions = [
    { value: '', label: 'All clients' },
    ...users.filter((u) => u.role === 'CLIENT').map((u) => ({ value: String(u.id), label: u.full_name })),
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">Every project across the platform, scoped to what your role can see.</p>
        <Button size="sm" leftIcon={<Plus className="size-4" />} onClick={() => setIsCreateOpen(true)}>
          New Project
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className="relative lg:col-span-2">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <Input
            type="search"
            placeholder="Search by title…"
            aria-label="Search projects"
            className="pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select aria-label="Filter by status" options={statusOptions} value={status} onChange={(e) => setStatus(e.target.value as ProjectStatus | '')} />
        <Select aria-label="Filter by priority" options={priorityOptions} value={priority} onChange={(e) => setPriority(e.target.value as ProjectPriority | '')} />
        <Select aria-label="Filter by service" options={serviceOptions} value={serviceId} onChange={(e) => setServiceId(e.target.value)} />
      </div>
      <div className="grid gap-3 sm:max-w-xs">
        <Select aria-label="Filter by client" options={clientOptions} value={clientId} onChange={(e) => setClientId(e.target.value)} />
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState title="Couldn't load projects" message="We had trouble reaching the server. Please try again." onRetry={() => refetch()} />
      ) : !projects || projects.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title={hasFilters ? 'No projects match your filters' : 'No projects yet'}
          description={hasFilters ? 'Try a different search or filter.' : 'Create the first project to get started.'}
        />
      ) : (
        <div className={cn('transition-opacity', isFetching && 'opacity-60')}>
          <Table>
            <TableHead>
              <TableHeaderCell>Title</TableHeaderCell>
              <TableHeaderCell>Client</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Priority</TableHeaderCell>
              <TableHeaderCell>Budget</TableHeaderCell>
              <TableHeaderCell>Deadline</TableHeaderCell>
            </TableHead>
            <TableBody>
              {projects.map((project) => (
                <TableRow key={project.id} clickable onClick={() => navigate(detailPath(project.id))}>
                  <TableCell className="font-medium text-slate-900">{project.title}</TableCell>
                  <TableCell>{usersMap.get(project.client_id)?.full_name ?? `#${project.client_id}`}</TableCell>
                  <TableCell>
                    <Badge variant={projectStatusVariant[project.status]}>{formatEnumLabel(project.status)}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={projectPriorityVariant[project.priority]}>{formatEnumLabel(project.priority)}</Badge>
                  </TableCell>
                  <TableCell>{formatMoney(project.budget) ?? '—'}</TableCell>
                  <TableCell>{formatDate(project.deadline)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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

      <CreateProjectModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        clients={users}
        onCreated={(project) => {
          setIsCreateOpen(false)
          navigate(detailPath(project.id))
        }}
      />
    </div>
  )
}
