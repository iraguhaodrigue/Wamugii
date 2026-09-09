import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { paths, roleHomePath } from '@/routes/paths'
import { Button, Input } from '@/components/ui'
import type { ApiError } from '@/lib/apiClient'

const schema = z.object({
  full_name: z.string().min(1, 'Full name is required'),
  email: z.string().email('Enter a valid email address'),
  phone: z.string().optional(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormValues = z.infer<typeof schema>

export function Register() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()
  const [formError, setFormError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues) => {
    setFormError(null)
    try {
      const user = await registerUser({
        full_name: values.full_name,
        email: values.email,
        phone: values.phone || null,
        password: values.password,
      })
      navigate(roleHomePath[user.role], { replace: true })
    } catch (err) {
      setFormError((err as ApiError).message ?? 'Unable to create your account. Please try again.')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-slate-900">Create your account</h1>
        <p className="text-sm text-slate-500">Get started with WAMUGII TECH SOLUTIONS</p>
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
          hint="At least 8 characters"
          error={errors.password?.message}
          {...register('password')}
        />

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <Button type="submit" isLoading={isSubmitting} className="w-full">
          Create account
        </Button>
      </form>

      <p className="text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link to={paths.login} className="font-medium text-brand-400 hover:text-brand-300 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
