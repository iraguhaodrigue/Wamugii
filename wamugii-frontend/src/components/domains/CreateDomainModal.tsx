import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  DEFAULT_REGISTRAR,
  createDomain,
  totalFee,
  type Domain,
} from '@/api/domains'
import { listHostingAccounts } from '@/api/hosting'
import type { UserRead } from '@/api/users'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'
import { formatMoney } from '@/utils/format'

interface DomainFormValues {
  client_id: string
  hosting_account_id: string
  domain_name: string
  registrar: string
  registration_fee: string
  service_fee: string
  registered_date: string
  expires_at: string
  nameservers: string
  notes: string
}

export interface CreateDomainModalProps {
  isOpen: boolean
  onClose: () => void
  clients: UserRead[]
  onCreated: (domain: Domain) => void
}

export function CreateDomainModal({
  isOpen,
  onClose,
  clients,
  onCreated,
}: CreateDomainModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<DomainFormValues>({
    defaultValues: {
      client_id: '',
      hosting_account_id: '',
      domain_name: '',
      registrar: DEFAULT_REGISTRAR,
      registration_fee: '0',
      service_fee: '0',
      registered_date: '',
      expires_at: '',
      nameservers: '',
      notes: '',
    },
  })

  const clientId = watch('client_id')
  const registrationFee = watch('registration_fee')
  const serviceFee = watch('service_fee')

  // Hosting accounts are scoped to the chosen client: the backend rejects a
  // link to another client's account (422), so never offer one.
  const { data: hostingAccounts } = useQuery({
    queryKey: ['hosting', 'accounts', 'domain-form', clientId],
    queryFn: () => listHostingAccounts({ client_id: Number(clientId), limit: 100 }),
    enabled: Boolean(clientId),
  })

  const mutation = useMutation({
    mutationFn: (values: DomainFormValues) =>
      createDomain({
        client_id: Number(values.client_id),
        hosting_account_id: values.hosting_account_id
          ? Number(values.hosting_account_id)
          : null,
        domain_name: values.domain_name.trim(),
        registrar: values.registrar.trim() || DEFAULT_REGISTRAR,
        registration_fee: values.registration_fee || '0',
        service_fee: values.service_fee || null,
        status: 'PENDING',
        registered_date: values.registered_date || null,
        expires_at: values.expires_at || null,
        auto_renew: false,
        nameservers: values.nameservers.trim() || null,
        notes: values.notes.trim() || null,
        invoice_id: null,
      }),
    onSuccess: (domain) => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
      setFormError(null)
      onCreated(domain)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  const clientOptions = [
    { value: '', label: 'Select a client' },
    ...clients
      .filter((u) => u.role === 'CLIENT' && u.is_active)
      .map((u) => ({ value: String(u.id), label: `${u.full_name} (${u.email})` })),
  ]
  const hostingOptions = [
    { value: '', label: 'No hosting link — domain only' },
    ...(hostingAccounts ?? []).map((a) => ({
      value: String(a.id),
      label: a.domain ?? `Hosting #${a.id}`,
    })),
  ]

  const total = totalFee(registrationFee, serviceFee)

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Register a Domain" size="lg">
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
            label="Hosting account"
            options={hostingOptions}
            disabled={!clientId}
            hint="Optional — link this domain to their hosting"
            {...register('hosting_account_id')}
          />
          <Input
            label="Domain name"
            required
            placeholder="example.rw"
            error={errors.domain_name?.message}
            {...register('domain_name', { required: 'Enter the domain name' })}
          />
          <Input label="Registrar" {...register('registrar')} />
          <Input
            label="Registration fee (RWF)"
            type="number"
            step="0.01"
            min="0"
            hint="What the registrar charged"
            {...register('registration_fee')}
          />
          <Input
            label="Service fee (RWF)"
            type="number"
            step="0.01"
            min="0"
            hint="Your fee for handling it — may be 0"
            {...register('service_fee')}
          />
          <Input label="Registered date" type="date" hint="Optional" {...register('registered_date')} />
          <Input label="Expires at" type="date" hint="Optional" {...register('expires_at')} />
        </div>

        <Textarea
          label="Nameservers"
          rows={2}
          hint="Optional — can be filled in after registration"
          {...register('nameservers')}
        />
        <Textarea
          label="Internal notes"
          rows={2}
          hint="Staff only — never shown to the client"
          {...register('notes')}
        />

        <dl className="space-y-1.5 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">
          <div className="flex justify-between">
            <dt className="text-slate-500">Total to invoice</dt>
            <dd className="font-semibold text-slate-900">{formatMoney(total)}</dd>
          </div>
          <p className="pt-1 text-xs text-slate-500">
            Registration + service fee. The domain starts as Pending and the client is emailed
            now; raise the invoice from the detail page.
          </p>
        </dl>

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
            Register Domain
          </Button>
        </div>
      </form>
    </Modal>
  )
}
