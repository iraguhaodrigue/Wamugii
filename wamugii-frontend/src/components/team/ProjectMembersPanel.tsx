import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, UserMinus, Users } from 'lucide-react'
import {
  addProjectMember,
  listProjectMembers,
  removeProjectMember,
  updateProjectMemberRole,
  type ProjectMember,
} from '@/api/teamMembers'
import { PROJECT_ROLES, type ProjectRole } from '@/api/team'
import { useUsersMap } from '@/hooks/useUsersMap'
import type { ApiError } from '@/lib/apiClient'
import {
  Badge,
  Button,
  ConfirmDialog,
  EmptyState,
  ErrorState,
  Modal,
  Select,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { projectRoleVariant, roleVariant } from '@/utils/statusBadge'

export interface ProjectMembersPanelProps {
  projectId: number
}

/**
 * Who is working on this project, for ADMIN/STAFF.
 *
 * Assigning someone emails them the project title and their role — never the
 * client or the budget, which the backend enforces in
 * `services/email_templates.project_assignment_member`.
 */
export function ProjectMembersPanel({ projectId }: ProjectMembersPanelProps) {
  const queryClient = useQueryClient()
  const { users } = useUsersMap()

  const [isAddOpen, setIsAddOpen] = useState(false)
  const [newUserId, setNewUserId] = useState('')
  const [newRole, setNewRole] = useState<ProjectRole>('PROGRAMMER')
  const [removing, setRemoving] = useState<ProjectMember | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const membersQuery = useQuery({
    queryKey: ['projects', projectId, 'members'],
    queryFn: () => listProjectMembers(projectId),
  })

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'members'] })
  }

  const addMutation = useMutation<ProjectMember, ApiError, void>({
    mutationFn: () =>
      addProjectMember(projectId, {
        user_id: Number(newUserId),
        project_role: newRole,
      }),
    onSuccess: () => {
      refresh()
      setIsAddOpen(false)
      setNewUserId('')
      setNewRole('PROGRAMMER')
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const roleMutation = useMutation<
    ProjectMember,
    ApiError,
    { memberId: number; project_role: ProjectRole }
  >({
    mutationFn: ({ memberId, project_role }) =>
      updateProjectMemberRole(projectId, memberId, { project_role }),
    onSuccess: () => {
      refresh()
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const removeMutation = useMutation<ProjectMember, ApiError, number>({
    mutationFn: (memberId) => removeProjectMember(projectId, memberId),
    onSuccess: () => {
      refresh()
      setRemoving(null)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const members = membersQuery.data ?? []
  const assignedIds = new Set(members.map((m) => m.user_id))

  // Only approved, active TEAM_MEMBERs and STAFF can be assigned — the backend
  // 422s anything else, so don't offer it. Already-assigned users drop out of
  // the list so the picker can't be used to re-add somebody twice.
  const candidates = users.filter(
    (u) =>
      (u.role === 'TEAM_MEMBER' || u.role === 'STAFF') &&
      u.is_active &&
      u.approval_status === 'APPROVED' &&
      !assignedIds.has(u.id),
  )

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Collaborators on this project. They see the brief, milestones and files — never the
          client, the budget or any invoice.
        </p>
        <Button
          size="sm"
          className="shrink-0"
          leftIcon={<Plus className="size-4" />}
          onClick={() => {
            setFormError(null)
            setIsAddOpen(true)
          }}
        >
          Assign member
        </Button>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      {membersQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : membersQuery.isError ? (
        <ErrorState
          title="Couldn't load the team"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => membersQuery.refetch()}
        />
      ) : members.length === 0 ? (
        <EmptyState
          icon={Users}
          title="Nobody assigned yet"
          description="Assign a team member and they'll see this project in their own dashboard."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Member</TableHeaderCell>
            <TableHeaderCell>Account</TableHeaderCell>
            <TableHeaderCell>Project role</TableHeaderCell>
            <TableHeaderCell>Assigned</TableHeaderCell>
            <TableHeaderCell>Actions</TableHeaderCell>
          </TableHead>
          <TableBody>
            {members.map((member) => (
              <TableRow key={member.id}>
                <TableCell className="font-medium text-slate-900">
                  {member.user_full_name ?? `#${member.user_id}`}
                  {member.user_email && (
                    <span className="block text-xs font-normal text-slate-500">
                      {member.user_email}
                    </span>
                  )}
                </TableCell>
                <TableCell>
                  {member.user_role && (
                    <Badge variant={roleVariant[member.user_role as 'STAFF' | 'TEAM_MEMBER']}>
                      {formatEnumLabel(member.user_role)}
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Badge variant={projectRoleVariant[member.project_role]}>
                      {formatEnumLabel(member.project_role)}
                    </Badge>
                    <Select
                      aria-label={`Change role for ${member.user_full_name ?? member.user_id}`}
                      className="h-8 w-40 text-xs"
                      options={PROJECT_ROLES.map((r) => ({
                        value: r,
                        label: formatEnumLabel(r),
                      }))}
                      value={member.project_role}
                      disabled={roleMutation.isPending}
                      onChange={(e) =>
                        roleMutation.mutate({
                          memberId: member.id,
                          project_role: e.target.value as ProjectRole,
                        })
                      }
                    />
                  </div>
                </TableCell>
                <TableCell>{formatDate(member.assigned_at)}</TableCell>
                <TableCell>
                  <Button
                    size="sm"
                    variant="outline"
                    leftIcon={<UserMinus className="size-4" />}
                    onClick={() => setRemoving(member)}
                  >
                    Remove
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Modal
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        title="Assign a member to this project"
        size="md"
      >
        <div className="space-y-4">
          <Select
            label="Member"
            required
            options={[
              { value: '', label: 'Select a member' },
              ...candidates.map((u) => ({
                value: String(u.id),
                label: `${u.full_name} (${formatEnumLabel(u.role)})`,
              })),
            ]}
            value={newUserId}
            onChange={(e) => setNewUserId(e.target.value)}
            hint={
              candidates.length === 0
                ? 'No approved team members left to assign — approve one under Team Members first.'
                : 'Approved team members and staff only'
            }
          />
          <Select
            label="Project role"
            options={PROJECT_ROLES.map((r) => ({ value: r, label: formatEnumLabel(r) }))}
            value={newRole}
            onChange={(e) => setNewRole(e.target.value as ProjectRole)}
          />

          <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
            They&apos;ll be notified and emailed the project title, their role and the deadline.
            No client or billing detail is included.
          </p>

          {formError && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {formError}
            </p>
          )}

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsAddOpen(false)}
              disabled={addMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              disabled={!newUserId}
              isLoading={addMutation.isPending}
              onClick={() => addMutation.mutate()}
            >
              Assign
            </Button>
          </div>
        </div>
      </Modal>

      <ConfirmDialog
        isOpen={removing !== null}
        onClose={() => setRemoving(null)}
        onConfirm={() => removing && removeMutation.mutate(removing.id)}
        title={`Remove ${removing?.user_full_name ?? 'this member'}?`}
        description="The project disappears from their dashboard straight away. Their assignment history is kept, and you can add them back later."
        confirmLabel="Remove"
        isDanger
        isLoading={removeMutation.isPending}
      />
    </div>
  )
}
