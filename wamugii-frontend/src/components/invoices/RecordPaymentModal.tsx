import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation } from '@tanstack/react-query'
import { PAYMENT_METHODS, recordPayment, type PaymentMethod } from '@/api/invoices'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'
import { formatEnumLabel, formatMoney } from '@/utils/format'

interface PaymentFormValues {
  amount: string
  payment_date: string
  method: PaymentMethod
  reference: string
  notes: string
}

export interface RecordPaymentModalProps {
  isOpen: boolean
  onClose: () => void
  invoiceId: number
  /** Decimal string — shown as the maximum the backend will accept. */
  balanceDue: string
  onRecorded: () => void
}

export function RecordPaymentModal({
  isOpen,
  onClose,
  invoiceId,
  balanceDue,
  onRecorded,
}: RecordPaymentModalProps) {
  const [formError, setFormError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PaymentFormValues>({
    defaultValues: { amount: '', payment_date: '', method: 'MOBILE_MONEY', reference: '', notes: '' },
  })

  const mutation = useMutation({
    mutationFn: (values: PaymentFormValues) =>
      recordPayment(invoiceId, {
        amount: values.amount,
        payment_date: values.payment_date
          ? new Date(`${values.payment_date}T00:00:00Z`).toISOString()
          : null,
        method: values.method,
        reference: values.reference || null,
        notes: values.notes || null,
      }),
    onSuccess: () => {
      reset()
      setFormError(null)
      onRecorded()
    },
    // Covers 422 (payment exceeds balance) and 409 (paid/cancelled invoice).
    onError: (err: ApiError) => setFormError(err.message),
  })

  function handleClose() {
    reset()
    setFormError(null)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Record a payment" size="md">
      <form onSubmit={handleSubmit((values) => mutation.mutate(values))} className="space-y-4" noValidate>
        <p className="text-sm text-slate-500">
          Records money already received. Outstanding balance:{' '}
          <span className="font-medium text-slate-900">{formatMoney(balanceDue)}</span>
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Amount"
            type="number"
            step="0.01"
            min="0"
            required
            error={errors.amount?.message}
            {...register('amount', { required: 'Enter the amount received' })}
          />
          <Input label="Payment date" type="date" hint="Defaults to today" {...register('payment_date')} />
        </div>

        <Select
          label="Method"
          options={PAYMENT_METHODS.map((m) => ({ value: m, label: formatEnumLabel(m) }))}
          {...register('method')}
        />

        <Input
          label="Reference"
          hint="Optional — e.g. a mobile money transaction ID"
          {...register('reference')}
        />

        <Textarea label="Internal notes" rows={2} hint="Staff only — never shown to the client" {...register('notes')} />

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={handleClose} disabled={mutation.isPending}>
            Cancel
          </Button>
          <Button type="submit" isLoading={mutation.isPending}>
            Record Payment
          </Button>
        </div>
      </form>
    </Modal>
  )
}
