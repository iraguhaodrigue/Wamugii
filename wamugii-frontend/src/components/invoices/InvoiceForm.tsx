import { useQuery } from '@tanstack/react-query'
import { useFieldArray, useForm } from 'react-hook-form'
import { Plus, Trash2 } from 'lucide-react'
import { listProjects } from '@/api/projects'
import { SETTABLE_INVOICE_STATUSES, type InvoiceStatus } from '@/api/invoices'
import type { UserRead } from '@/api/users'
import { Button, Input, Select, Textarea } from '@/components/ui'
import { formatEnumLabel, formatMoney } from '@/utils/format'

export interface InvoiceFormValues {
  client_id: string
  project_id: string
  issue_date: string
  due_date: string
  status: InvoiceStatus
  tax: string
  discount: string
  notes: string
  items: { description: string; quantity: string; unit_price: string }[]
}

export interface InvoiceFormProps {
  clients: UserRead[]
  defaultValues?: Partial<InvoiceFormValues>
  mode: 'create' | 'edit'
  /**
   * PAID/CANCELLED invoices: the backend rejects every field except `notes`
   * with 409, so everything else is disabled rather than letting the user
   * fill in a form that cannot be saved.
   */
  notesOnly?: boolean
  isSaving?: boolean
  formError?: string | null
  onSubmit: (values: InvoiceFormValues) => void
  onCancel: () => void
}

const EMPTY_ITEM = { description: '', quantity: '1', unit_price: '0' }

function toNumber(value: string): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

export function InvoiceForm({
  clients,
  defaultValues,
  mode,
  notesOnly = false,
  isSaving = false,
  formError,
  onSubmit,
  onCancel,
}: InvoiceFormProps) {
  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<InvoiceFormValues>({
    defaultValues: {
      client_id: '',
      project_id: '',
      issue_date: '',
      due_date: '',
      status: 'DRAFT',
      tax: '',
      discount: '',
      notes: '',
      items: [{ ...EMPTY_ITEM }],
      ...defaultValues,
    },
  })

  const { fields, append, remove } = useFieldArray({ control, name: 'items' })

  const clientId = watch('client_id')
  const items = watch('items')
  const tax = watch('tax')
  const discount = watch('discount')

  // Projects are scoped to the chosen client: the backend rejects an invoice
  // whose project belongs to a different client (422), so never offer one.
  const { data: projects } = useQuery({
    queryKey: ['projects', 'invoice-form', clientId],
    queryFn: () => listProjects({ client_id: Number(clientId), limit: 100 }),
    enabled: Boolean(clientId),
  })

  const subtotal = (items ?? []).reduce(
    (sum, item) => sum + toNumber(item.quantity) * toNumber(item.unit_price),
    0,
  )
  const total = Math.max(subtotal - toNumber(discount) + toNumber(tax), 0)

  const clientOptions = [
    { value: '', label: 'Select a client' },
    ...clients
      .filter((u) => u.role === 'CLIENT' && u.is_active)
      .map((u) => ({ value: String(u.id), label: `${u.full_name} (${u.email})` })),
  ]

  const projectOptions = [
    { value: '', label: 'No project — standalone invoice' },
    ...(projects ?? []).map((p) => ({ value: String(p.id), label: p.title })),
  ]

  const statusOptions = SETTABLE_INVOICE_STATUSES.map((s) => ({
    value: s,
    label: formatEnumLabel(s),
  }))

  const disabled = notesOnly || isSaving

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
      {notesOnly && (
        <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          This invoice is settled or cancelled, so its amounts are locked. Only the internal note can
          be changed.
        </p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <Select
          label="Client"
          required
          options={clientOptions}
          disabled={disabled || mode === 'edit'}
          hint={mode === 'edit' ? 'The client cannot be changed after creation' : undefined}
          error={errors.client_id?.message}
          {...register('client_id', { required: 'Select a client' })}
        />
        <Select
          label="Project"
          options={projectOptions}
          disabled={disabled || !clientId}
          hint="Optional — leave blank for a standalone invoice (e.g. a one-off sale)"
          {...register('project_id')}
        />
        <Input label="Issue date" type="date" hint="Defaults to today" disabled={disabled} {...register('issue_date')} />
        <Input label="Due date" type="date" hint="Optional" disabled={disabled} {...register('due_date')} />
        <Select
          label="Status"
          options={statusOptions}
          disabled={disabled}
          hint="Paid / Partially paid / Overdue are set automatically from the amounts"
          {...register('status')}
        />
      </div>

      <div className="space-y-3 border-t border-slate-100 pt-5">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Line items</h3>
          {!disabled && (
            <Button
              type="button"
              size="sm"
              variant="outline"
              leftIcon={<Plus className="size-4" />}
              onClick={() => append({ ...EMPTY_ITEM })}
            >
              Add line
            </Button>
          )}
        </div>

        {fields.length === 0 && (
          <p className="text-sm text-slate-500">
            No line items — the invoice total will be zero until you add one.
          </p>
        )}

        {fields.map((field, index) => {
          const lineTotal =
            toNumber(items?.[index]?.quantity ?? '0') * toNumber(items?.[index]?.unit_price ?? '0')
          return (
            <div key={field.id} className="grid items-end gap-3 sm:grid-cols-[1fr_auto_auto_auto_auto]">
              <Input
                label={index === 0 ? 'Description' : undefined}
                aria-label="Line description"
                disabled={disabled}
                {...register(`items.${index}.description` as const)}
              />
              <Input
                label={index === 0 ? 'Qty' : undefined}
                aria-label="Quantity"
                type="number"
                step="0.01"
                min="0"
                className="w-24"
                disabled={disabled}
                {...register(`items.${index}.quantity` as const)}
              />
              <Input
                label={index === 0 ? 'Unit price' : undefined}
                aria-label="Unit price"
                type="number"
                step="0.01"
                min="0"
                className="w-32"
                disabled={disabled}
                {...register(`items.${index}.unit_price` as const)}
              />
              <div className="pb-2.5 text-sm font-medium text-slate-900">
                {formatMoney(lineTotal.toFixed(2)) ?? '—'}
              </div>
              {!disabled && (
                <button
                  type="button"
                  onClick={() => remove(index)}
                  aria-label={`Remove line ${index + 1}`}
                  className="mb-1 rounded-lg p-2 text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600"
                >
                  <Trash2 className="size-4" />
                </button>
              )}
            </div>
          )
        })}
      </div>

      <div className="grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-2">
        <Input label="Tax" type="number" step="0.01" min="0" hint="Optional" disabled={disabled} {...register('tax')} />
        <Input
          label="Discount"
          type="number"
          step="0.01"
          min="0"
          hint="Optional"
          disabled={disabled}
          {...register('discount')}
        />
      </div>

      {/* Preview only — the backend recomputes subtotal from the line items and
          ignores any subtotal/total sent in the body. */}
      <dl className="space-y-1.5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">
        <div className="flex justify-between">
          <dt className="text-slate-500">Subtotal</dt>
          <dd className="font-medium text-slate-900">{formatMoney(subtotal.toFixed(2))}</dd>
        </div>
        {toNumber(discount) > 0 && (
          <div className="flex justify-between">
            <dt className="text-slate-500">Discount</dt>
            <dd className="font-medium text-slate-900">−{formatMoney(toNumber(discount).toFixed(2))}</dd>
          </div>
        )}
        {toNumber(tax) > 0 && (
          <div className="flex justify-between">
            <dt className="text-slate-500">Tax</dt>
            <dd className="font-medium text-slate-900">{formatMoney(toNumber(tax).toFixed(2))}</dd>
          </div>
        )}
        <div className="flex justify-between border-t border-slate-200 pt-1.5">
          <dt className="font-semibold text-slate-900">Total</dt>
          <dd className="font-semibold text-slate-900">{formatMoney(total.toFixed(2))}</dd>
        </div>
      </dl>

      <Textarea
        label="Internal notes"
        rows={3}
        hint="Staff only — never shown to the client"
        {...register('notes')}
      />

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <div className="flex justify-end gap-2 border-t border-slate-100 pt-4">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isSaving}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSaving}>
          {mode === 'create' ? 'Create Invoice' : 'Save Changes'}
        </Button>
      </div>
    </form>
  )
}

/** Shared mapping from form strings to the API payload shape. */
export function toItemsPayload(values: InvoiceFormValues) {
  return values.items
    .filter((item) => item.description.trim().length > 0)
    .map((item) => ({
      description: item.description.trim(),
      quantity: item.quantity || '1',
      unit_price: item.unit_price || '0',
    }))
}

/** Dates come out of `<input type="date">` as YYYY-MM-DD; the API wants ISO. */
export function toIsoDate(value: string): string | null {
  if (!value) return null
  const date = new Date(`${value}T00:00:00Z`)
  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}
