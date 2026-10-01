import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link } from 'react-router-dom'
import { MailCheck } from 'lucide-react'
import { registerTeamMember } from '@/api/teamMembers'
import { paths } from '@/routes/paths'
import { Button, Input } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

// Mirrors MIN_PASSWORD_LENGTH in app/schemas/user.py — the backend is the real
// check, this just saves a round trip.
const MIN_PASSWORD_LENGTH = 8

const schema = z.object({
  full_name: z.string().min(2, 'Enter your full name'),
  email: z.string().email('Enter a valid email address'),
  phone: z.string().optional(),
  password: z
    .string()
    .min(MIN_PASSWORD_LENGTH, `Password must be at least ${MIN_PASSWORD_LENGTH} characters`),
})

type FormValues = z.infer<typeof schema>

/**
 * Public self-registration for project collaborators.
 *
 * Deliberately not a login: the account is created PENDING and can't reach
 * anything until an admin approves it, so there's nothing to log in to yet.
 * That's why this shows a confirmation instead of redirecting to a dashboard,
 * unlike the client Register page.
 */
export function JoinTeam() {
  const [submitted, setSubmitted] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      const result = await registerTeamMember({
        full_name: values.full_name.trim(),
        email: values.email.trim(),
        phone: values.phone?.trim() || null,
        password: values.password,
      })
      setSubmitted(result.detail)
    } catch (err) {
      setFormError((err as ApiError).message ?? 'Unable to register. Please try again.')
    }
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="flex size-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <MailCheck className="size-6" aria-hidden="true" />
        </div>
        <div className="space-y-1">
          <h1 className="text-xl font-semibold text-slate-900">Registration received</h1>
          <p className="text-sm text-slate-500">{submitted}</p>
        </div>
        <Link
          to={paths.login}
          className="text-sm font-medium text-brand-600 hover:text-brand-700 hover:underline"
        >
          Back to login
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Join as a team member</h1>
        <p className="text-sm text-slate-500">
          For interns and collaborators working on WAMUGII projects. An admin reviews every
          registration.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
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
          hint="Optional"
          error={errors.phone?.message}
          {...register('phone')}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="new-password"
          required
          hint={`At least ${MIN_PASSWORD_LENGTH} characters`}
          error={errors.password?.message}
          {...register('password')}
        />

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting} className="w-full">
          Request access
        </Button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Looking for a quote instead?{' '}
        <Link
          to={paths.register}
          className="font-medium text-brand-400 hover:text-brand-300 hover:underline"
        >
          Create a client account
        </Link>
      </p>
    </div>
  )
}
