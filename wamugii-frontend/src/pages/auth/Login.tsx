import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { isPathAllowedForRole, paths, roleHomePath } from '@/routes/paths'
import { Button, Input } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

const schema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
})

type FormValues = z.infer<typeof schema>

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      const user = await login(values.email, values.password)
      const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname
      const destination = from && isPathAllowedForRole(from, user.role) ? from : roleHomePath[user.role]
      navigate(destination, { replace: true })
    } catch (err) {
      setFormError((err as ApiError).message ?? 'Unable to log in. Please try again.')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Welcome back</h1>
        <p className="text-sm text-slate-500">Log in to your WAMUGII account</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          required
          error={errors.email?.message}
          {...register('email')}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          error={errors.password?.message}
          {...register('password')}
        />

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting} className="w-full">
          Log in
        </Button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Don&apos;t have an account?{' '}
        <Link to={paths.register} className="font-medium text-blue-600 hover:underline">
          Create one
        </Link>
      </p>
    </div>
  )
}
