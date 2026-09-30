import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createInvoice, type InvoiceRead } from '@/api/invoices'
import type { UserRead } from '@/api/users'
import type { ApiError } from '@/lib/apiClient'
import { Modal } from '@/components/ui'
import {
  InvoiceForm,
  toIsoDate,
  toItemsPayload,
  toTaxPayload,
  type InvoiceFormValues,
} from './InvoiceForm'

export interface CreateInvoiceModalProps {
  isOpen: boolean
  onClose: () => void
  clients: UserRead[]
  onCreated: (invoice: InvoiceRead) => void
  /**
   * Prefill for callers that already know what's being billed — e.g. the
   * hosting account detail page opens this with the client and a line item for
   * the plan at the right price for its billing cycle.
   */
  defaultValues?: Partial<InvoiceFormValues>
}

export function CreateInvoiceModal({
  isOpen,
  onClose,
  clients,
  onCreated,
  defaultValues,
}: CreateInvoiceModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (values: InvoiceFormValues) =>
      createInvoice({
        client_id: Number(values.client_id),
        project_id: values.project_id ? Number(values.project_id) : null,
        issue_date: toIsoDate(values.issue_date),
        due_date: toIsoDate(values.due_date),
        // The backend recomputes subtotal from the items; this is only the
        // required field placeholder for the generated type.
        subtotal: '0',
        ...toTaxPayload(values),
        discount: values.discount || null,
        status: values.status,
        notes: values.notes || null,
        items: toItemsPayload(values),
      }),
    onSuccess: (invoice) => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      queryClient.invalidateQueries({ queryKey: ['admin', 'dashboard'] })
      setFormError(null)
      onCreated(invoice)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  function handleClose() {
    setFormError(null)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="New Invoice" size="lg">
      {/* Remount per open so the form resets between invoices. */}
      <InvoiceForm
        key={isOpen ? 'open' : 'closed'}
        mode="create"
        clients={clients}
        defaultValues={defaultValues}
        isSaving={mutation.isPending}
        formError={formError}
        onSubmit={(values) => mutation.mutate(values)}
        onCancel={handleClose}
      />
    </Modal>
  )
}
