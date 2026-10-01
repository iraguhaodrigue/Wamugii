import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { TICKET_CATEGORIES, createClientTicket, type ClientTicket, type TicketCategory } from '@/api/support'
import { listClientProjects } from '@/api/clientPortal'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'
import { formatEnumLabel } from '@/utils/format'

interface TicketFormValues {
  subject: string
  description: string
  category: TicketCategory
  project_id: string
}

export interface ClientCreateTicketModalProps {
  isOpen: boolean
  onClose: () => void
  onCreated: (ticket: ClientTicket) => void
}

/** Client-side "New Ticket". Priority is ours to set, so it isn't offered here. */
export function ClientCreateTicketModal({
  isOpen,
  onClose,
  onCreated,
}: ClientCreateTicketModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TicketFormValues>({
    defaultValues: { subject: '', description: '', category: 'GENERAL', project_id: '' },
  })

  // Their own projects only — the backend 422s a ticket pointed at someone
  // else's project, so never offer one.
  const { data: projects } = useQuery({
    queryKey: ['client', 'projects', 'ticket-form'],
    queryFn: () => listClientProjects({ limit: 100 }),
    enabled: isOpen,
  })

  const mutation = useMutation<ClientTicket, ApiError, TicketFormValues>({
    mutationFn: (values) =>
      createClientTicket({
        subject: values.subject.trim(),
        description: values.description.trim(),
        category: values.category,
        project_id: values.project_id ? Number(values.project_id) : null,
      }),
    onSuccess: (ticket) => {
      queryClient.invalidateQueries({ queryKey: ['client', 'tickets'] })
      setFormError(null)
      onCreated(ticket)
    },
    onError: (err) => setFormError(err.message),
  })

  const projectOptions = [
    { value: '', label: 'Not about a specific project' },
    ...(projects ?? []).map((p) => ({ value: String(p.id), label: p.title })),
  ]

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Open a Support Ticket" size="lg">
      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="space-y-4"
        noValidate
      >
        <Input
          label="Subject"
          required
          placeholder="Short summary of what you need"
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
            label="Related project"
            options={projectOptions}
            hint="Optional"
            {...register('project_id')}
          />
        </div>

        <Textarea
          label="How can we help?"
          required
          rows={6}
          placeholder="Tell us what's happening, and anything we'd need to reproduce it."
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
            Submit Ticket
          </Button>
        </div>
      </form>
    </Modal>
  )
}
