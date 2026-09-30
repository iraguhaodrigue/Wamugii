import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Pencil, Plus, Server, Trash2 } from 'lucide-react'
import {
  deactivateHostingPlan,
  listHostingPlans,
  type HostingPlan,
} from '@/api/hosting'
import { usePageTitle } from '@/context/PageTitleContext'
import {
  Badge,
  Button,
  ConfirmDialog,
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
import { HostingPlanModal } from '@/components/hosting/HostingPlanModal'
import { formatMoney } from '@/utils/format'

export function AdminHostingPlans() {
  usePageTitle('Hosting Plans')
  const queryClient = useQueryClient()

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editing, setEditing] = useState<HostingPlan | null>(null)
  const [pendingDelete, setPendingDelete] = useState<HostingPlan | null>(null)

  // Inactive plans are shown here so an admin can see what they've retired.
  const plansQuery = useQuery({
    queryKey: ['hosting', 'plans', 'admin'],
    queryFn: () => listHostingPlans(true),
  })

  const deleteMutation = useMutation({
    mutationFn: (planId: number) => deactivateHostingPlan(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosting'] })
      setPendingDelete(null)
    },
  })

  const plans = plansQuery.data ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          The plans clients can subscribe to. These appear on the public hosting page.
        </p>
        <Button
          size="sm"
          leftIcon={<Plus className="size-4" />}
          onClick={() => {
            setEditing(null)
            setIsModalOpen(true)
          }}
        >
          New Plan
        </Button>
      </div>

      {plansQuery.isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : plansQuery.isError ? (
        <ErrorState
          title="Couldn't load hosting plans"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => plansQuery.refetch()}
        />
      ) : plans.length === 0 ? (
        <EmptyState
          icon={Server}
          title="No hosting plans yet"
          description="Create the first plan to show it on the public hosting page."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Order</TableHeaderCell>
            <TableHeaderCell>Plan</TableHeaderCell>
            <TableHeaderCell>Monthly</TableHeaderCell>
            <TableHeaderCell>Yearly</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>
              <span className="sr-only">Actions</span>
            </TableHeaderCell>
          </TableHead>
          <TableBody>
            {plans.map((plan) => (
              <TableRow key={plan.id}>
                <TableCell className="text-slate-500">{plan.display_order}</TableCell>
                <TableCell>
                  <p className="font-medium text-slate-900">{plan.name}</p>
                  <p className="mt-0.5 max-w-md truncate text-xs text-slate-500">{plan.features}</p>
                </TableCell>
                <TableCell>{formatMoney(plan.monthly_price) ?? '—'}</TableCell>
                <TableCell>{formatMoney(plan.yearly_price) ?? '—'}</TableCell>
                <TableCell>
                  <Badge variant={plan.is_active ? 'success' : 'neutral'}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center justify-end gap-1">
                    <button
                      type="button"
                      onClick={() => {
                        setEditing(plan)
                        setIsModalOpen(true)
                      }}
                      aria-label={`Edit ${plan.name}`}
                      className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900"
                    >
                      <Pencil className="size-4" />
                    </button>
                    {plan.is_active && (
                      <button
                        type="button"
                        onClick={() => setPendingDelete(plan)}
                        aria-label={`Deactivate ${plan.name}`}
                        className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <HostingPlanModal
        // Remount per open so the form picks up the plan being edited.
        key={editing?.id ?? 'new'}
        isOpen={isModalOpen}
        plan={editing}
        onClose={() => setIsModalOpen(false)}
        onSaved={() => setIsModalOpen(false)}
      />

      <ConfirmDialog
        isOpen={pendingDelete !== null}
        onClose={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && deleteMutation.mutate(pendingDelete.id)}
        title="Deactivate this plan?"
        description={
          pendingDelete
            ? `"${pendingDelete.name}" will stop appearing on the public hosting page. Existing hosting accounts on it are not affected.`
            : undefined
        }
        confirmLabel="Deactivate"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
