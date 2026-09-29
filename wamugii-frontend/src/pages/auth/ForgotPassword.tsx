import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ArrowLeft, MailCheck } from 'lucide-react'
import { forgotPassword, type MessageResponse } from '@/api/auth'
import { paths } from '@/routes/paths'
import { Button, Input } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
})

type FormValues = z.infer<typeof schema>

export function ForgotPassword() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const mutation = useMutation<MessageResponse, ApiError, FormValues>({
    mutationFn: (values) => forgotPassword(values.email),
  })

  // The backend deliberately returns the same response whether or not the
  // address exists, so this screen must never imply either way.
  if (mutation.isSuccess) {
    return (
      <div className="flex flex-col gap-6 text-center">
        <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <MailCheck className="size-6" aria-hidden="true" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-semibold text-slate-900">Check your inbox</h1>
          <p className="text-sm text-slate-500">
            If an account exists for that email, you&apos;ll receive a reset link shortly. Check
            your inbox and spam folder.
          </p>
          <p className="text-xs text-slate-400">The link expires in 1 hour.</p>
        </div>
        <Link
          to={paths.login}
          className="inline-flex items-center justify-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to log in
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Forgot your password?</h1>
        <p className="text-sm text-slate-500">
          Enter your email and we&apos;ll send you a link to reset it.
        </p>
      </div>

      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="flex flex-col gap-4"
        noValidate
      >
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          required
          error={errors.email?.message}
          {...register('email')}
        />

        {mutation.isError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {mutation.error?.message ?? 'Something went wrong. Please try again.'}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting || mutation.isPending} className="w-full">
          Send Reset Link
        </Button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Remembered it?{' '}
        <Link to={paths.login} className="font-medium text-brand-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
