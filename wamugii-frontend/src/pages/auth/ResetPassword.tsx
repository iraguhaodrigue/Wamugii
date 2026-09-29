import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { Link, Navigate, useSearchParams } from 'react-router-dom'
import { CheckCircle2, ShieldAlert } from 'lucide-react'
import { resetPassword, type MessageResponse } from '@/api/auth'
import { paths } from '@/routes/paths'
import { Button, Input } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

const schema = z
  .object({
    password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(1, 'Confirm your new password'),
  })
  .refine((values) => values.password === values.confirm_password, {
    path: ['confirm_password'],
    message: "Passwords don't match",
  })

type FormValues = z.infer<typeof schema>

export function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const mutation = useMutation<MessageResponse, ApiError, FormValues>({
    mutationFn: (values) => resetPassword(token ?? '', values.password),
  })

  // No token means the link was mistyped or opened directly — send them to
  // request a fresh one rather than showing a form that cannot succeed.
  if (!token) {
    return <Navigate to={paths.forgotPassword} replace />
  }

  if (mutation.isSuccess) {
    return (
      <div className="flex flex-col gap-6 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-green-50 text-green-600">
          <CheckCircle2 className="size-6" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-slate-900">Password reset successfully</h1>
          <p className="text-sm text-slate-500">You can now log in with your new password.</p>
        </div>
        <Link
          to={paths.login}
          className="inline-flex h-10 items-center justify-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
        >
          Go to log in
        </Link>
      </div>
    )
  }

  // 400 is the backend's single "expired / already used / unknown" answer.
  const error = mutation.error
  const isLinkDead = error?.status === 400

  if (isLinkDead) {
    return (
      <div className="flex flex-col gap-6 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-amber-50 text-amber-600">
          <ShieldAlert className="size-6" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-slate-900">This link no longer works</h1>
          <p className="text-sm text-slate-500">
            This reset link has expired or has already been used.
          </p>
        </div>
        <Link
          to={paths.forgotPassword}
          className="inline-flex h-10 items-center justify-center rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white shadow-[var(--shadow-glow-brand)] transition-[filter] hover:brightness-110"
        >
          Request a new link
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Set a new password</h1>
        <p className="text-sm text-slate-500">Choose a new password for your WAMUGII account.</p>
      </div>

      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-4"
        noValidate
      >
        <Input
          label="New password"
          type="password"
          autoComplete="new-password"
          required
          hint="At least 8 characters"
          error={errors.password?.message}
          {...register('password')}
        />
        <Input
          label="Confirm new password"
          type="password"
          autoComplete="new-password"
          required
          error={errors.confirm_password?.message}
          {...register('confirm_password')}
        />

        {mutation.isError && !isLinkDead && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error?.message ?? 'Something went wrong. Please try again.'}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting || mutation.isPending} className="w-full">
          Reset Password
        </Button>
      </form>

      <p className="text-center text-sm text-slate-500">
        <Link to={paths.login} className="font-medium text-brand-600 hover:underline">
          Back to log in
        </Link>
      </p>
    </div>
  )
}
