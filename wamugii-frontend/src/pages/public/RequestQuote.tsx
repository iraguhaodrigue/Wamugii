import { useEffect, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { CheckCircle2, Send, Server } from 'lucide-react'
import {
  createQuoteRequest,
  type QuoteAnswerSubmit,
  type QuoteRequestCreate,
  type QuoteRequestPublicRead,
} from '@/api/quoteRequests'
import { listServiceQuestions, listServices } from '@/api/services'
import { paths } from '@/routes/paths'
import { Button, Container, Input, Select, Skeleton, Textarea } from '@/components/ui'
import { QuestionField, type AnswerMap } from '@/components/services/QuestionField'
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

/**
 * The label a chosen hosting plan is filed under on the quote.
 *
 * It travels as an answer with no `question_id` — the mechanism the backend
 * keeps for a detail the form captured without a configured question behind it.
 * That way staff see which plan was picked in the same list as every other
 * answer, with no extra column and no plan text buried in the description.
 */
const PLAN_ANSWER_LABEL = 'Selected hosting plan'

export function RequestQuote() {
  const [searchParams] = useSearchParams()
  // `?service=` accepts an id or a slug: the hosting page links with
  // `?service=hosting`, and the domain pages with `?service=domain`, so matching
  // on id alone silently preselected nothing.
  const serviceParam = searchParams.get('service') ?? ''
  const planParam = searchParams.get('plan') ?? ''

  const [answers, setAnswers] = useState<AnswerMap>({})
  const [answerErrors, setAnswerErrors] = useState<Record<number, string>>({})

  const { data: services } = useQuery({
    queryKey: ['services', 'quote-form'],
    queryFn: () => listServices(),
  })

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      service_id: '',
      // A plan deep-link already says what this is about, so start the title off
      // for them. Fully editable.
      project_title: planParam ? `Hosting — ${planParam} plan` : '',
    },
  })

  const selectedServiceId = watch('service_id')

  /** The id behind `?service=`, whether it arrived as an id or a slug. */
  const resolvedParamServiceId = useMemo(() => {
    if (!serviceParam || !services) return ''
    const needle = serviceParam.toLowerCase()
    const match =
      services.find((s) => String(s.id) === serviceParam) ??
      services.find((s) => s.slug.toLowerCase() === needle) ??
      // Loose fallback so "hosting" finds "Hosting & Domains".
      services.find((s) => s.slug.toLowerCase().includes(needle)) ??
      services.find((s) => s.name.toLowerCase().includes(needle))
    return match ? String(match.id) : ''
  }, [serviceParam, services])

  useEffect(() => {
    if (resolvedParamServiceId) setValue('service_id', resolvedParamServiceId)
  }, [resolvedParamServiceId, setValue])

  const { data: questions, isLoading: isLoadingQuestions } = useQuery({
    queryKey: ['services', selectedServiceId, 'questions'],
    queryFn: () => listServiceQuestions(selectedServiceId!),
    enabled: Boolean(selectedServiceId),
  })

  // Switching service makes the previous service's answers meaningless, and
  // leaving them in state would submit question ids the backend rejects.
  useEffect(() => {
    setAnswers({})
    setAnswerErrors({})
  }, [selectedServiceId])

  const mutation = useMutation<QuoteRequestPublicRead, ApiError, FormValues>({
    mutationFn: (values) => {
      const submitted: QuoteAnswerSubmit[] = (questions ?? [])
        .map((question) => ({
          question_id: question.id,
          answer: (answers[question.id] ?? '').trim(),
        }))
        .filter((entry) => entry.answer.length > 0)

      if (planParam) {
        submitted.push({ question_text: PLAN_ANSWER_LABEL, answer: planParam })
      }

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
        answers: submitted,
      }
      return createQuoteRequest(payload)
    },
  })

  /**
   * Required questions, checked before the request goes out.
   *
   * The backend enforces the same rule and is the real gate — this just saves a
   * round trip and points at the field that needs attention.
   */
  function validateAnswers(): boolean {
    const missing: Record<number, string> = {}
    for (const question of questions ?? []) {
      if (question.is_required && !(answers[question.id] ?? '').trim()) {
        missing[question.id] = 'This answer is required'
      }
    }
    setAnswerErrors(missing)
    return Object.keys(missing).length === 0
  }

  if (mutation.isSuccess) {
    return (
      <Container className="py-20">
        <div className="mx-auto max-w-lg rounded-xl border border-slate-200 bg-panel p-8 text-center shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-10">
          <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-green-50 text-green-600">
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
              className="inline-flex h-11 items-center justify-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-5 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
            >
              Back to Home
            </Link>
            <Link
              to={paths.services}
              className="inline-flex h-11 items-center justify-center rounded-lg border border-slate-300 px-5 text-sm font-semibold text-slate-400 hover:bg-slate-100"
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
  const selectedService = services?.find((s) => String(s.id) === selectedServiceId)
  const hasQuestions = (questions?.length ?? 0) > 0

  return (
    <Container className="py-16 sm:py-20">
      <div className="mx-auto max-w-2xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Request a Quote</h1>
          <p className="mt-4 text-base text-slate-500">
            Tell us about your project. No account needed — we'll follow up by email or phone with next steps.
          </p>
        </div>

        {planParam && (
          <div className="mt-8 flex items-start gap-3 rounded-xl border border-brand-200 bg-brand-50 p-4">
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand-100 text-brand-700">
              <Server className="size-4" aria-hidden="true" />
            </div>
            <div className="min-w-0 text-sm">
              <p className="font-semibold text-slate-900">
                Hosting plan: <span className="text-brand-700">{planParam}</span>
              </p>
              <p className="mt-0.5 text-slate-500">
                We'll include this with your request.{' '}
                <Link to={paths.hosting} className="font-medium text-brand-600 hover:text-brand-700">
                  Change plan
                </Link>
              </p>
            </div>
          </div>
        )}

        <form
          onSubmit={handleSubmit((values) => {
            if (!validateAnswers()) return
            mutation.mutate(values)
          })}
          className="mt-12 space-y-8 rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm sm:p-8"
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

          {/* The adaptive part: whatever this service asks about. A service with
              no questions renders nothing here and the form behaves as before. */}
          {selectedServiceId && isLoadingQuestions && (
            <div className="space-y-4 border-t border-slate-100 pt-8">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-10 rounded-lg" />
              <Skeleton className="h-10 rounded-lg" />
            </div>
          )}

          {hasQuestions && (
            <div className="space-y-5 border-t border-slate-100 pt-8">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                  About your {selectedService?.name ?? 'project'}
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  A few questions specific to this service, so we can quote accurately.
                </p>
              </div>
              {questions!.map((question) => (
                <QuestionField
                  key={question.id}
                  question={question}
                  value={answers[question.id] ?? ''}
                  error={answerErrors[question.id]}
                  disabled={mutation.isPending}
                  onChange={(value) => {
                    setAnswers((prev) => ({ ...prev, [question.id]: value }))
                    setAnswerErrors((prev) => {
                      if (!prev[question.id]) return prev
                      const next = { ...prev }
                      delete next[question.id]
                      return next
                    })
                  }}
                />
              ))}
            </div>
          )}

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
