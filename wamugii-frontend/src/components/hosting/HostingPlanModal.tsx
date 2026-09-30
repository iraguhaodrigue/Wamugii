import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  createHostingPlan,
  updateHostingPlan,
  type HostingPlan,
} from '@/api/hosting'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Textarea } from '@/components/ui'

interface PlanFormValues {
  name: string
  description: string
  features: string
  monthly_price: string
  yearly_price: string
  display_order: string
}

export interface HostingPlanModalProps {
  isOpen: boolean
  onClose: () => void
  /** Present when editing; absent when creating. */
  plan?: HostingPlan | null
  onSaved: () => void
}

export function HostingPlanModal({ isOpen, onClose, plan, onSaved }: HostingPlanModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)
  const isEdit = Boolean(plan)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PlanFormValues>({
    defaultValues: {
      name: plan?.name ?? '',
      description: plan?.description ?? '',
      features: plan?.features ?? '',
      monthly_price: plan?.monthly_price ?? '0',
      yearly_price: plan?.yearly_price ?? '0',
      display_order: String(plan?.display_order ?? 0),
    },
  })

  const mutation = useMutation({
    mutationFn: (values: PlanFormValues) => {
      const fields = {
        name: values.name.trim(),
        description: values.description.trim() || null,
        features: values.features.trim(),
        monthly_price: values.monthly_price || '0',
        yearly_price: values.yearly_price || '0',
        display_order: Number(values.display_order) || 0,
      }
      // `is_active` is only sent on create. Omitting it on edit leaves a
      // deactivated plan deactivated — sending `true` would silently revive it.
      return isEdit
        ? updateHostingPlan(plan!.id, fields)
        : createHostingPlan({ ...fields, is_active: true })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hosting'] })
      setFormError(null)
      reset()
      onSaved()
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  function handleClose() {
    setFormError(null)
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEdit ? `Edit ${plan?.name}` : 'New Hosting Plan'}
      size="lg"
    >
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="space-y-4"
        noValidate
      >
        <Input
          label="Plan name"
          required
          error={errors.name?.message}
          {...register('name', { required: 'Plan name is required' })}
        />
        <Input label="Description" hint="Optional — a short line under the plan name" {...register('description')} />
        <Textarea
          label="Features"
          rows={3}
          hint="Comma separated — each item becomes a bullet on the pricing page"
          {...register('features')}
        />

        <div className="grid gap-4 sm:grid-cols-3">
          <Input
            label="Monthly price (RWF)"
            type="number"
            step="0.01"
            min="0"
            {...register('monthly_price')}
          />
          <Input
            label="Yearly price (RWF)"
            type="number"
            step="0.01"
            min="0"
            {...register('yearly_price')}
          />
          <Input
            label="Display order"
            type="number"
            min="0"
            hint="Lowest first"
            {...register('display_order')}
          />
        </div>

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
          <Button type="button" variant="outline" onClick={handleClose} disabled={mutation.isPending}>
            Cancel
          </Button>
          <Button type="submit" isLoading={mutation.isPending}>
            {isEdit ? 'Save Changes' : 'Create Plan'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
