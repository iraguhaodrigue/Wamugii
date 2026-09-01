import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle2, Send } from 'lucide-react'
import { createQuoteRequest, type QuoteRequestCreate, type QuoteRequestPublicRead } from '@/api/quoteRequests'
import { listServices } from '@/api/services'
import { paths } from '@/routes/paths'
import { Button, Container, Input, Select, Textarea } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

const schema = z.object({
  full_name: z.string().min(1, 'Full name is required'),
  email: z.string().email('Enter a valid email address'),
  phone: z.string().min(1, 'Phone number is required'),
  company_name: z.string().optional(),
  service_id: z.string().optional(),
  project_title: z.string().min(1, 'Project title is required'),
  project_description: z.string().min(10, 'Please tell us a bit more about your project (10+ characters)'),
  budget_range: z.string().optional(),
  preferred_deadline: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

export function RequestQuote() {
  const [searchParams] = useSearchParams()
  const preselectedServiceId = searchParams.get('service') ?? ''

  const { data: services } = useQuery({
    queryKey: ['services', 'quote-form'],
    queryFn: () => listServices(),
  })

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { service_id: preselectedServiceId },
  })

  useEffect(() => {
    if (preselectedServiceId && services?.some((s) => String(s.id) === preselectedServiceId)) {
      setValue('service_id', preselectedServiceId)
    }
  }, [preselectedServiceId, services, setValue])

  const mutation = useMutation<QuoteRequestPublicRead, ApiError, FormValues>({
    mutationFn: (values) => {
      const payload: QuoteRequestCreate = {
        full_name: values.full_name,
        email: values.email,
        phone: values.phone,
        company_name: values.company_name || null,
        service_id: values.service_id ? Number(values.service_id) : null,
        project_title: values.project_title,
        project_description: values.project_description,
        budget_range: values.budget_range || null,
        preferred_deadline: values.preferred_deadline || null,
      }
      return createQuoteRequest(payload)
    },
  })

  if (mutation.isSuccess) {
    return (
      <Container className="py-20">
        <div className="mx-auto max-w-lg rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm sm:p-10">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
            <CheckCircle2 className="size-7" aria-hidden="true" />
          </div>
          <h1 className="mt-6 text-2xl font-bold text-slate-900">Request received</h1>
          <p className="mt-3 text-sm text-slate-500">
            Thanks, {mutation.data.full_name.split(' ')[0]} — we've received your request for &ldquo;
            {mutation.data.project_title}&rdquo;. Our team will review it and get back to you at{' '}
            <span className="font-medium text-slate-700">{mutation.data.email}</span> shortly.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Link
              to={paths.home}
              className="inline-flex h-11 items-center justify-center rounded-lg bg-brand-600 px-5 text-sm font-semibold text-white shadow-sm shadow-brand-900/10 hover:bg-brand-700"
            >
              Back to Home
            </Link>
            <Link
              to={paths.services}
              className="inline-flex h-11 items-center justify-center rounded-lg border border-slate-300 px-5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Explore Services
            </Link>
          </div>
        </div>
      </Container>
    )
  }

  const serviceOptions = [
    { value: '', label: 'General inquiry (no specific service)' },
    ...(services?.map((s) => ({ value: String(s.id), label: s.name })) ?? []),
  ]

  return (
    <Container className="py-16 sm:py-20">
      <div className="mx-auto max-w-2xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Request a Quote</h1>
          <p className="mt-4 text-base text-slate-500">
            Tell us about your project. No account needed — we'll follow up by email or phone with next steps.
          </p>
        </div>

        <form
          onSubmit={handleSubmit((values) => mutation.mutate(values))}
          className="mt-12 space-y-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
          noValidate
        >
          <div className="space-y-5">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Your details</h2>
            <div className="grid gap-5 sm:grid-cols-2">
              <Input
                label="Full name"
                autoComplete="name"
                required
                error={errors.full_name?.message}
                {...register('full_name')}
              />
              <Input
                label="Email"
                type="email"
                autoComplete="email"
                required
                error={errors.email?.message}
                {...register('email')}
              />
              <Input
                label="Phone"
                type="tel"
                autoComplete="tel"
                required
                error={errors.phone?.message}
                {...register('phone')}
              />
              <Input
                label="Company name"
                autoComplete="organization"
                hint="Optional"
                error={errors.company_name?.message}
                {...register('company_name')}
              />
            </div>
          </div>

          <div className="space-y-5 border-t border-slate-100 pt-8">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Project details</h2>
            <Select
              label="Related service"
              hint="Optional — pick the closest match, or leave as a general inquiry"
              options={serviceOptions}
              error={errors.service_id?.message}
              {...register('service_id')}
            />
            <Input
              label="Project title"
              required
              error={errors.project_title?.message}
              {...register('project_title')}
            />
            <Textarea
              label="Project description"
              required
              rows={5}
              hint="What are you trying to build or fix? The more detail, the better."
              error={errors.project_description?.message}
              {...register('project_description')}
            />
            <div className="grid gap-5 sm:grid-cols-2">
              <Input
                label="Budget range"
                placeholder="e.g. RWF 1,000,000 – 3,000,000"
                hint="Optional"
                error={errors.budget_range?.message}
                {...register('budget_range')}
              />
              <Input
                label="Preferred deadline"
                placeholder="e.g. Within 2 months"
                hint="Optional"
                error={errors.preferred_deadline?.message}
                {...register('preferred_deadline')}
              />
            </div>
          </div>

          {mutation.isError && (
            <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
              {mutation.error.message}
            </p>
          )}

          <Button type="submit" size="lg" isLoading={isSubmitting || mutation.isPending} className="w-full" leftIcon={<Send className="size-4" />}>
            Submit Request
          </Button>
        </form>
      </div>
    </Container>
  )
}
