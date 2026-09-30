import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  BILLING_CYCLES,
  createHostingAccount,
  listHostingPlans,
  previewNextBillingDate,
  priceForCycle,
  type BillingCycle,
  type HostingAccount,
} from '@/api/hosting'
import type { UserRead } from '@/api/users'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'
import { formatDate, formatEnumLabel, formatMoney } from '@/utils/format'

interface AccountFormValues {
  client_id: string
  plan_id: string
  domain: string
  billing_cycle: BillingCycle
  start_date: string
  expires_at: string
  server_notes: string
}

export interface CreateHostingAccountModalProps {
  isOpen: boolean
  onClose: () => void
  clients: UserRead[]
  onCreated: (account: HostingAccount) => void
}

export function CreateHostingAccountModal({
  isOpen,
  onClose,
  clients,
  onCreated,
}: CreateHostingAccountModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const { data: plans } = useQuery({
    queryKey: ['hosting', 'plans', 'form'],
    queryFn: () => listHostingPlans(),
    enabled: isOpen,
  })

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AccountFormValues>({
    defaultValues: {
      client_id: '',
      plan_id: '',
      domain: '',
      billing_cycle: 'MONTHLY',
      start_date: '',
      expires_at: '',
      server_notes: '',
    },
  })

  const startDate = watch('start_date')
  const cycle = watch('billing_cycle')
  const planId = watch('plan_id')

  // Preview only — the server recomputes and stores its own value.
  const nextBilling = startDate ? previewNextBillingDate(startDate, cycle) : null
  const selectedPlan = (plans ?? []).find((p) => String(p.id) === planId)

  const mutation = useMutation({
    mutationFn: (values: AccountFormValues) =>
      createHostingAccount({
        client_id: Number(values.client_id),
        plan_id: Number(values.plan_id),
        domain: values.domain.trim() || null,
        billing_cycle: values.billing_cycle,
        start_date: values.start_date || null,
        expires_at: values.expires_at || null,
        server_notes: values.server_notes.trim() || null,
        status: 'PENDING',
      }),
    onSuccess: (account) => {
      queryClient.invalidateQueries({ queryKey: ['hosting'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      setFormError(null)
      onCreated(account)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const clientOptions = [
    { value: '', label: 'Select a client' },
    ...clients
      .filter((u) => u.role === 'CLIENT' && u.is_active)
      .map((u) => ({ value: String(u.id), label: `${u.full_name} (${u.email})` })),
  ]
  const planOptions = [
    { value: '', label: 'Select a plan' },
    ...(plans ?? []).map((p) => ({ value: String(p.id), label: p.name })),
  ]

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="New Hosting Account" size="lg">
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="space-y-4"
        noValidate
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Client"
            required
            options={clientOptions}
            error={errors.client_id?.message}
            {...register('client_id', { required: 'Select a client' })}
          />
          <Select
            label="Plan"
            required
            options={planOptions}
            error={errors.plan_id?.message}
            {...register('plan_id', { required: 'Select a plan' })}
          />
          <Input label="Domain" hint="Optional — the primary domain" {...register('domain')} />
          <Select
            label="Billing cycle"
            options={BILLING_CYCLES.map((c) => ({ value: c, label: formatEnumLabel(c) }))}
            {...register('billing_cycle')}
          />
          <Input label="Start date" type="date" hint="Optional" {...register('start_date')} />
          <Input label="Expires at" type="date" hint="Optional" {...register('expires_at')} />
        </div>

        <Textarea
          label="Internal notes"
          rows={2}
          hint="Staff only — never shown to the client"
          {...register('server_notes')}
        />

        {(nextBilling || selectedPlan) && (
          <dl className="space-y-1.5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">
            {selectedPlan && (
              <div className="flex justify-between">
                <dt className="text-slate-500">{formatEnumLabel(cycle)} price</dt>
                <dd className="font-medium text-slate-900">
                  {formatMoney(priceForCycle(selectedPlan, cycle))}
                </dd>
              </div>
            )}
            {nextBilling && (
              <div className="flex justify-between">
                <dt className="text-slate-500">Next billing date</dt>
                <dd className="font-medium text-slate-900">{formatDate(nextBilling)}</dd>
              </div>
            )}
            <p className="pt-1 text-xs text-slate-500">
              The account starts as Pending. The client is emailed now, and again when you mark it
              Active.
            </p>
          </dl>
        )}

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
          <Button type="button" variant="outline" onClick={onClose} disabled={mutation.isPending}>
            Cancel
          </Button>
          <Button type="submit" isLoading={mutation.isPending}>
            Create Account
          </Button>
        </div>
      </form>
    </Modal>
  )
}
