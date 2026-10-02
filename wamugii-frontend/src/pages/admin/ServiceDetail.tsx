import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ExternalLink, SearchX } from 'lucide-react'
import { getService, updateService, type Service } from '@/api/services'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import {
  Badge,
  Button,
  EmptyState,
  ErrorState,
  Skeleton,
  Textarea,
} from '@/components/ui'
import { ServiceQuestionsPanel } from '@/components/services/ServiceQuestionsPanel'
import { cn } from '@/utils/cn'

type Tab = 'content' | 'questions'

/**
 * Admin editing for one service: the public detail-page copy, and the questions
 * its quote form asks.
 *
 * Only the fields this pass added are editable here — name, slug, pricing and
 * category are set by the seed script and left alone, so this screen can't
 * accidentally rename a service or break a public URL.
 */
export function AdminServiceDetail() {
  const { serviceId } = useParams<{ serviceId: string }>()
  const queryClient = useQueryClient()

  const [tab, setTab] = useState<Tab>('content')
  // null means "not edited" so the stored value keeps showing through.
  const [longDraft, setLongDraft] = useState<string | null>(null)
  const [featuresDraft, setFeaturesDraft] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const serviceQuery = useQuery<Service, ApiError>({
    queryKey: ['services', 'detail', serviceId],
    queryFn: () => getService(serviceId!),
    enabled: Boolean(serviceId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  const service = serviceQuery.data
  usePageTitle(service?.name ?? 'Service')

  const saveMutation = useMutation<Service, ApiError, { long_description?: string | null; features?: string[] | null }>({
    mutationFn: (payload) => updateService(serviceId!, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(['services', 'detail', serviceId], updated)
      queryClient.invalidateQueries({ queryKey: ['services'] })
      setLongDraft(null)
      setFeaturesDraft(null)
      setFormError(null)
    },
    onError: (err) => setFormError(err.message),
  })

  if (serviceQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = serviceQuery.isError && serviceQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Service not found"
        description="This service doesn't exist."
        action={
          <Link
            to={paths.admin.services}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Services
          </Link>
        }
      />
    )
  }

  if (serviceQuery.isError || !service) {
    return (
      <ErrorState
        title="Couldn't load this service"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => serviceQuery.refetch()}
      />
    )
  }

  // One feature per line while editing; the API takes and returns a list.
  const storedFeatures = (service.features ?? []).join('\n')
  const currentLong = longDraft ?? (service.long_description ?? '')
  const currentFeatures = featuresDraft ?? storedFeatures
  const isDirty =
    (longDraft !== null && longDraft !== (service.long_description ?? '')) ||
    (featuresDraft !== null && featuresDraft !== storedFeatures)

  const tabs: { key: Tab; label: string }[] = [
    { key: 'content', label: 'Detail page' },
    { key: 'questions', label: 'Quote questions' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={paths.admin.services}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Services
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{service.name}</h1>
            {service.category && <Badge variant="brand">{service.category}</Badge>}
            {!service.is_active && <Badge variant="neutral">Hidden</Badge>}
          </div>
          <Link
            to={paths.serviceDetail(service.id)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700"
          >
            View public page
            <ExternalLink className="size-4" aria-hidden="true" />
          </Link>
        </div>
      </div>

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {formError}
        </p>
      )}

      <div className="border-b border-slate-200">
        <nav className="-mb-px flex gap-6" aria-label="Service detail tabs">
          {tabs.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={cn(
                'border-b-2 px-1 pb-3 text-sm font-medium transition-colors',
                tab === t.key
                  ? 'border-brand-600 text-brand-600'
                  : 'border-transparent text-slate-500 hover:text-slate-700',
              )}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      {tab === 'content' && (
        <div className="space-y-6">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Public detail page
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Both fields are optional. Left empty, the public page shows just the short
              description and the existing description, exactly as it did before.
            </p>

            <div className="mt-5 space-y-5">
              <Textarea
                label="Long description"
                rows={8}
                hint="The “explore” write-up, shown under the existing description. Line breaks are kept."
                value={currentLong}
                onChange={(e) => setLongDraft(e.target.value)}
              />
              <Textarea
                label="Features"
                rows={7}
                hint="One per line — rendered as the “What's included” checklist."
                value={currentFeatures}
                onChange={(e) => setFeaturesDraft(e.target.value)}
              />
              <p className="text-xs text-slate-500">
                {currentFeatures.split('\n').map((l) => l.trim()).filter(Boolean).length} feature(s).
                Blank lines are ignored.
              </p>
            </div>

            {isDirty && (
              <div className="mt-5 flex justify-end gap-2 border-t border-slate-100 pt-4">
                <Button
                  variant="outline"
                  onClick={() => {
                    setLongDraft(null)
                    setFeaturesDraft(null)
                  }}
                  disabled={saveMutation.isPending}
                >
                  Cancel
                </Button>
                <Button
                  isLoading={saveMutation.isPending}
                  onClick={() =>
                    saveMutation.mutate({
                      long_description: currentLong.trim() || null,
                      features: currentFeatures
                        .split('\n')
                        .map((line) => line.trim())
                        .filter(Boolean),
                    })
                  }
                >
                  Save changes
                </Button>
              </div>
            )}
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Existing copy
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Set by the seed script and shown here for context — edit it there, not from this
              screen, so a public slug can never be changed by accident.
            </p>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Slug</dt>
                <dd className="font-mono text-slate-900">{service.slug}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Short description</dt>
                <dd className="text-slate-700">{service.short_description ?? '—'}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Description</dt>
                <dd className="whitespace-pre-line text-slate-700">{service.description ?? '—'}</dd>
              </div>
            </dl>
          </div>
        </div>
      )}

      {tab === 'questions' && <ServiceQuestionsPanel serviceId={service.id} />}
    </div>
  )
}
