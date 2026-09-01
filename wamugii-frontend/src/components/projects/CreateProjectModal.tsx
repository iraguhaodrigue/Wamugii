import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createProject, type ProjectRead } from '@/api/projects'
import { listServices } from '@/api/services'
import type { UserRead } from '@/api/users'
import type { ApiError } from '@/lib/apiClient'
import { Button, Input, Modal, Select, Textarea } from '@/components/ui'

const schema = z.object({
  client_id: z.string().min(1, 'Select a client'),
  service_id: z.string().optional(),
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']),
  budget: z.string().optional(),
  start_date: z.string().optional(),
  deadline: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export interface CreateProjectModalProps {
  isOpen: boolean
  onClose: () => void
  clients: UserRead[]
  onCreated: (project: ProjectRead) => void
}

export function CreateProjectModal({ isOpen, onClose, clients, onCreated }: CreateProjectModalProps) {
  const queryClient = useQueryClient()
  const [formError, setFormError] = useState<string | null>(null)

  const { data: services } = useQuery({
    queryKey: ['services', 'create-project-form'],
    queryFn: () => listServices(),
    enabled: isOpen,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { priority: 'MEDIUM' },
  })

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      createProject({
        client_id: Number(values.client_id),
        service_id: values.service_id ? Number(values.service_id) : null,
        title: values.title,
        description: values.description,
        priority: values.priority,
        budget: values.budget || null,
        start_date: values.start_date || null,
        deadline: values.deadline || null,
      }),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      reset()
      setFormError(null)
      onCreated(project)
    },
    onError: (err: ApiError) => setFormError(err.message),
  })

  function handleClose() {
    reset()
    setFormError(null)
    onClose()
  }

  const activeClients = clients.filter((c) => c.role === 'CLIENT' && c.is_active)
  const clientOptions = activeClients.map((c) => ({ value: String(c.id), label: `${c.full_name} (${c.email})` }))
  const serviceOptions = [
    { value: '', label: 'No related service' },
    ...(services?.map((s) => ({ value: String(s.id), label: s.name })) ?? []),
  ]
  const priorityOptions = [
    { value: 'LOW', label: 'Low' },
    { value: 'MEDIUM', label: 'Medium' },
    { value: 'HIGH', label: 'High' },
    { value: 'URGENT', label: 'Urgent' },
  ]

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="New Project" size="lg">
      <form onSubmit={handleSubmit((values) => mutation.mutate(values))} className="space-y-4" noValidate>
        {activeClients.length === 0 ? (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
            No active client accounts exist yet. A client must register before you can create a project for them.
          </p>
        ) : (
          <Select
            label="Client"
            required
            options={clientOptions}
            placeholder="Select a client"
            error={errors.client_id?.message}
            {...register('client_id')}
          />
        )}

        <Select label="Related service" options={serviceOptions} hint="Optional" {...register('service_id')} />

        <Input label="Title" required error={errors.title?.message} {...register('title')} />
        <Textarea
          label="Description"
          required
          rows={4}
          error={errors.description?.message}
          {...register('description')}
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <Select label="Priority" options={priorityOptions} {...register('priority')} />
          <Input
            label="Budget"
            type="number"
            step="0.01"
            min="0"
            hint="Optional"
            error={errors.budget?.message}
            {...register('budget')}
          />
          <Input label="Start date" type="date" hint="Optional" {...register('start_date')} />
          <Input label="Deadline" type="date" hint="Optional" {...register('deadline')} />
        </div>

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={handleClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting || mutation.isPending} disabled={activeClients.length === 0}>
            Create Project
          </Button>
        </div>
      </form>
    </Modal>
  )
}
