import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2 } from 'lucide-react'
import { getSettings, updateSettings, type CompanySettings } from '@/api/settings'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { Button, ErrorState, Input, Skeleton } from '@/components/ui'
import { formatDateTime } from '@/utils/format'

interface SettingsFormValues {
  company_name: string
  slogan: string
  tin: string
  address: string
  phone: string
  email: string
  website: string
  notification_email: string
}

function toFormValues(settings: CompanySettings): SettingsFormValues {
  return {
    company_name: settings.company_name ?? '',
    slogan: settings.slogan ?? '',
    tin: settings.tin ?? '',
    address: settings.address ?? '',
    phone: settings.phone ?? '',
    email: settings.email ?? '',
    website: settings.website ?? '',
    notification_email: settings.notification_email ?? '',
  }
}

/** Empty strings mean "clear this field", which the API expresses as null. */
function orNull(value: string): string | null {
  const trimmed = value.trim()
  return trimmed.length > 0 ? trimmed : null
}

export function AdminSettings() {
  usePageTitle('Settings')
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const settingsQuery = useQuery({ queryKey: ['settings'], queryFn: getSettings })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<SettingsFormValues>()

  // Populate once the settings arrive (and after a save, so the form matches
  // what the server actually stored).
  useEffect(() => {
    if (settingsQuery.data) reset(toFormValues(settingsQuery.data))
  }, [settingsQuery.data, reset])

  const mutation = useMutation({
    mutationFn: (values: SettingsFormValues) =>
      updateSettings({
        company_name: values.company_name.trim(),
        slogan: values.slogan.trim(),
        tin: orNull(values.tin),
        address: orNull(values.address),
        phone: orNull(values.phone),
        email: orNull(values.email),
        website: orNull(values.website),
        notification_email: orNull(values.notification_email),
      }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['settings'], updated)
      // Invoices render the company block from settings, so their cached
      // copies are now stale.
      queryClient.invalidateQueries({ queryKey: ['invoices'] })
      reset(toFormValues(updated))
      setFormError(null)
      setSaved(true)
    },
    onError: (err: ApiError) => {
      setSaved(false)
      setFormError(err.message)
    },
  })

  if (settingsQuery.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-4 w-64" />
        <Skeleton className="h-96 rounded-xl" />
      </div>
    )
  }

  if (settingsQuery.isError) {
    return (
      <ErrorState
        title="Couldn't load settings"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => settingsQuery.refetch()}
      />
    )
  }

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">
        Your company details. These appear on invoices and on the public site.
      </p>

      <form
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
        className="space-y-8"
        noValidate
      >
        <section className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Company profile
          </h2>
          <div className="mt-5 grid gap-5 sm:grid-cols-2">
            <Input
              label="Company name"
              required
              error={errors.company_name?.message}
              {...register('company_name', { required: 'Company name is required' })}
            />
            <Input label="Slogan" {...register('slogan')} />
            <Input
              label="TIN"
              hint="RRA Tax Identification Number — printed on VAT invoices"
              {...register('tin')}
            />
            <Input label="Phone" hint="Optional" {...register('phone')} />
            <Input
              label="Public email"
              type="email"
              hint="Shown on invoices and the public site"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input label="Website" hint="Optional" {...register('website')} />
            <div className="sm:col-span-2">
              <Input label="Address" hint="Optional" {...register('address')} />
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            Notifications
          </h2>
          <div className="mt-5 max-w-xl">
            <Input
              label="Quote notification email"
              type="email"
              hint="If set, new quote requests are emailed here instead of all staff. Leave blank to email every admin and staff member."
              error={errors.notification_email?.message}
              {...register('notification_email')}
            />
            <p className="mt-3 text-xs text-slate-500">
              This only changes where the <span className="font-medium">email</span> goes — every
              admin and staff member still sees new quotes in their notifications.
            </p>
          </div>
        </section>

        {formError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </p>
        )}

        <div className="flex items-center justify-end gap-3">
          {saved && !isDirty && (
            <span className="inline-flex items-center gap-1.5 text-sm font-medium text-green-600">
              <CheckCircle2 className="size-4" aria-hidden="true" />
              Saved
              {settingsQuery.data?.updated_at && (
                <span className="text-slate-500">
                  · {formatDateTime(settingsQuery.data.updated_at)}
                </span>
              )}
            </span>
          )}
          <Button type="submit" isLoading={mutation.isPending} disabled={!isDirty}>
            Save Changes
          </Button>
        </div>
      </form>
    </div>
  )
}
