import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { FolderKanban } from 'lucide-react'
import { listMyProjects } from '@/api/team'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { projectPriorityVariant, projectRoleVariant, projectStatusVariant } from '@/utils/statusBadge'

/** Every project this team member is assigned to. No client column — by design. */
export function TeamProjects() {
  const navigate = useNavigate()

  const {
    data: projects,
    isLoading,
    isError,
    refetch,
  } = useQuery({ queryKey: ['team', 'projects'], queryFn: listMyProjects })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">My Projects</h1>
        <p className="mt-1 text-sm text-slate-500">
          The projects you&apos;ve been assigned to, with your role on each.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
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
          title="No projects assigned"
          description="When the team assigns you to a project it'll appear here, and you'll get an email."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Project</TableHeaderCell>
            <TableHeaderCell>My role</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Priority</TableHeaderCell>
            <TableHeaderCell>Deadline</TableHeaderCell>
          </TableHead>
          <TableBody>
            {projects.map((project) => (
              <TableRow
                key={project.id}
                clickable
                onClick={() => navigate(paths.team.projectDetail(project.id))}
              >
                <TableCell className="font-medium text-slate-900">{project.title}</TableCell>
                <TableCell>
                  <Badge variant={projectRoleVariant[project.my_role]}>
                    {formatEnumLabel(project.my_role)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={projectStatusVariant[project.status]}>
                    {formatEnumLabel(project.status)}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={projectPriorityVariant[project.priority]}>
                    {formatEnumLabel(project.priority)}
                  </Badge>
                </TableCell>
                <TableCell>{formatDate(project.deadline)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
