import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Check, UserCheck, UserPlus, X } from 'lucide-react'
import {
  approveTeamMember,
  listPendingTeamMembers,
  listTeamMembers,
  rejectTeamMember,
  type UserRead,
} from '@/api/teamMembers'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Modal,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
  Textarea,
} from '@/components/ui'
import { formatDate } from '@/utils/format'
import { approvalStatusVariant } from '@/utils/statusBadge'

export function AdminTeamMembers() {
  usePageTitle('Team Members')
  const queryClient = useQueryClient()

  const [rejecting, setRejecting] = useState<UserRead | null>(null)
  const [reason, setReason] = useState('')
  const [formError, setFormError] = useState<string | null>(null)

  const pendingQuery = useQuery({
    queryKey: ['team-members', 'pending'],
    queryFn: listPendingTeamMembers,
  })

  const approvedQuery = useQuery({
    queryKey: ['team-members', 'approved'],
    queryFn: () => listTeamMembers({ approval_status: 'APPROVED' }),
  })

  function refresh() {
    queryClient.invalidateQueries({ queryKey: ['team-members'] })
    // The pending count on the dashboard moves with these.
    queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
    // The assignable-member picker on project detail only lists approved users.
    queryClient.invalidateQueries({ queryKey: ['users'] })
  }

  const approveMutation = useMutation<UserRead, ApiError, number>({
    mutationFn: (userId) => approveTeamMember(userId),
    onSuccess: () => {
      refresh()
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const rejectMutation = useMutation<UserRead, ApiError, { userId: number; reason: string }>({
    mutationFn: ({ userId, reason: note }) => rejectTeamMember(userId, note),
    onSuccess: () => {
      refresh()
      setRejecting(null)
      setReason('')
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  const pending = pendingQuery.data ?? []
  const approved = approvedQuery.data ?? []
  const isBusy = approveMutation.isPending || rejectMutation.isPending

  return (
    <div className="space-y-8">
      <p className="text-sm text-slate-500">
        Collaborators who registered at <span className="font-medium text-slate-700">/join</span>. An
        account can log in as soon as it&apos;s created but reaches nothing until you approve it, and
        it only ever sees the projects you assign it to — never a client or an invoice.
      </p>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <section>
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Awaiting approval
          </h2>
          {pending.length > 0 && <Badge variant="warning">{pending.length}</Badge>}
        </div>

        <div className="mt-4">
          {pendingQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-14 rounded-xl" />
              ))}
            </div>
          ) : pendingQuery.isError ? (
            <ErrorState
              title="Couldn't load pending registrations"
              message="We had trouble reaching the server. Please try again."
              onRetry={() => pendingQuery.refetch()}
            />
          ) : pending.length === 0 ? (
            <EmptyState
              icon={UserCheck}
              title="Nothing waiting"
              description="New team member registrations will appear here for approval."
            />
          ) : (
            <Table>
              <TableHead>
                <TableHeaderCell>Name</TableHeaderCell>
                <TableHeaderCell>Email</TableHeaderCell>
                <TableHeaderCell>Phone</TableHeaderCell>
                <TableHeaderCell>Registered</TableHeaderCell>
                <TableHeaderCell>Actions</TableHeaderCell>
              </TableHead>
              <TableBody>
                {pending.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell className="font-medium text-slate-900">
                      {member.full_name}
                    </TableCell>
                    <TableCell>{member.email}</TableCell>
                    <TableCell>{member.phone ?? '—'}</TableCell>
                    <TableCell>{formatDate(member.created_at)}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          leftIcon={<Check className="size-4" />}
                          disabled={isBusy}
                          isLoading={
                            approveMutation.isPending && approveMutation.variables === member.id
                          }
                          onClick={() => approveMutation.mutate(member.id)}
                        >
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          leftIcon={<X className="size-4" />}
                          disabled={isBusy}
                          onClick={() => {
                            setReason('')
                            setRejecting(member)
                          }}
                        >
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
          Approved team members
        </h2>

        <div className="mt-4">
          {approvedQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-14 rounded-xl" />
              ))}
            </div>
          ) : approvedQuery.isError ? (
            <ErrorState
              title="Couldn't load team members"
              message="We had trouble reaching the server. Please try again."
              onRetry={() => approvedQuery.refetch()}
            />
          ) : approved.length === 0 ? (
            <EmptyState
              icon={UserPlus}
              title="No team members yet"
              description="Approved collaborators show up here, ready to be assigned to projects."
            />
          ) : (
            <Table>
              <TableHead>
                <TableHeaderCell>Name</TableHeaderCell>
                <TableHeaderCell>Email</TableHeaderCell>
                <TableHeaderCell>Status</TableHeaderCell>
                <TableHeaderCell>Account</TableHeaderCell>
                <TableHeaderCell>Joined</TableHeaderCell>
              </TableHead>
              <TableBody>
                {approved.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell className="font-medium text-slate-900">
                      {member.full_name}
                    </TableCell>
                    <TableCell>{member.email}</TableCell>
                    <TableCell>
                      <Badge variant={approvalStatusVariant[member.approval_status]}>
                        Approved
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {member.is_active ? (
                        <span className="text-slate-600">Active</span>
                      ) : (
                        <Badge variant="neutral">Deactivated</Badge>
                      )}
                    </TableCell>
                    <TableCell>{formatDate(member.created_at)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </section>

      {/* A Modal rather than ConfirmDialog: the rejection note is a form field,
          and ConfirmDialog takes no children. */}
      <Modal
        isOpen={rejecting !== null}
        onClose={() => setRejecting(null)}
        title={`Reject ${rejecting?.full_name ?? 'registration'}?`}
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-500">
            They&apos;ll be emailed that the registration wasn&apos;t approved, and the account
            stays locked out of the app.
          </p>
          <Textarea
            label="Note for them (optional)"
            rows={3}
            hint="Included in the rejection email if you fill it in"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
            <Button
              variant="outline"
              onClick={() => setRejecting(null)}
              disabled={rejectMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              variant="danger"
              isLoading={rejectMutation.isPending}
              onClick={() =>
                rejecting && rejectMutation.mutate({ userId: rejecting.id, reason: reason.trim() })
              }
            >
              Reject registration
            </Button>
          </div>
        </div>
      </Modal>

    </div>
  )
}
