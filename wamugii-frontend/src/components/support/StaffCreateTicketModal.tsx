import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  TICKET_CATEGORIES,
  TICKET_PRIORITIES,
  createTicketForClient,
  type SupportTicket,
  type TicketCategory,
  type TicketPriority,
} from '@/api/support'
import { listProjects } from '@/api/projects'
import type { UserRead } from '@/api/users'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'
import { formatEnumLabel } from '@/utils/format'

interface TicketFormValues {
  client_id: string
  subject: string
  description: string
  category: TicketCategory
  priority: TicketPriority
  project_id: string
}

export interface StaffCreateTicketModalProps {
  isOpen: boolean
  onClose: () => void
  clients: UserRead[]
  onCreated: (ticket: SupportTicket) => void
}

/**
 * Raising a ticket on a client's behalf — for something that came in by phone
 * or email. The client is notified and emailed exactly as if they'd opened it.
 */
export function StaffCreateTicketModal({
  isOpen,
  onClose,
  clients,
  onCreated,
}: StaffCreateTicketModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<TicketFormValues>({
    defaultValues: {
      client_id: '',
      subject: '',
      description: '',
      category: 'GENERAL',
      priority: 'MEDIUM',
      project_id: '',
    },
  })

  const clientId = watch('client_id')

  // Projects are scoped to the chosen client: the backend rejects a ticket
  // pointed at another client's project (422), so never offer one.
  const { data: projects } = useQuery({
    queryKey: ['projects', 'ticket-form', clientId],
    queryFn: () => listProjects({ client_id: Number(clientId), limit: 100 }),
    enabled: Boolean(clientId),
  })

  const mutation = useMutation<SupportTicket, ApiError, TicketFormValues>({
    mutationFn: (values) =>
      createTicketForClient({
        client_id: Number(values.client_id),
        subject: values.subject.trim(),
        description: values.description.trim(),
        category: values.category,
        priority: values.priority,
        project_id: values.project_id ? Number(values.project_id) : null,
      }),
    onSuccess: (ticket) => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] })
      setFormError(null)
      onCreated(ticket)
    },
    onError: (err) => setFormError(err.message),
  })

  const clientOptions = [
    { value: '', label: 'Select a client' },
    ...clients
      .filter((u) => u.role === 'CLIENT' && u.is_active)
      .map((u) => ({ value: String(u.id), label: `${u.full_name} (${u.email})` })),
  ]
  const projectOptions = [
    { value: '', label: 'Not about a specific project' },
    ...(projects ?? []).map((p) => ({ value: String(p.id), label: p.title })),
  ]

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Raise a Ticket for a Client" size="lg">
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
            label="Related project"
            options={projectOptions}
            disabled={!clientId}
            hint="Optional"
            {...register('project_id')}
          />
        </div>

        <Input
          label="Subject"
          required
          error={errors.subject?.message}
          {...register('subject', { required: 'Enter a subject' })}
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <Select
            label="Category"
            options={TICKET_CATEGORIES.map((c) => ({ value: c, label: formatEnumLabel(c) }))}
            {...register('category')}
          />
          <Select
            label="Priority"
            options={TICKET_PRIORITIES.map((p) => ({ value: p, label: formatEnumLabel(p) }))}
            {...register('priority')}
          />
        </div>

        <Textarea
          label="Description"
          required
          rows={5}
          hint="This is the opening message the client sees — write it as they'd read it"
          error={errors.description?.message}
          {...register('description', { required: 'Describe the issue' })}
        />

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
            Create Ticket
          </Button>
        </div>
      </form>
    </Modal>
  )
}
