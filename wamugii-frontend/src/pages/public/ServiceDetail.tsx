import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Layers, SearchX } from 'lucide-react'
import { getService, type Service } from '@/api/services'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Container, EmptyState, ErrorState, Skeleton } from '@/components/ui'
import { formatMoney } from '@/utils/format'

export function ServiceDetail() {
  const { serviceId } = useParams<{ serviceId: string }>()

  const { data: service, isLoading, isError, error, refetch } = useQuery<Service, ApiError>({
    queryKey: ['services', 'detail', serviceId],
    queryFn: () => getService(serviceId!),
    enabled: Boolean(serviceId),
    retry: (failureCount, err) => err.status !== 404 && failureCount < 1,
  })

  const notFound = isError && error.status === 404

  if (isLoading) {
    return (
      <Container className="py-16 sm:py-20">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="mt-6 size-14 rounded-xl" />
        <Skeleton className="mt-6 h-10 w-2/3" />
        <Skeleton className="mt-4 h-4 w-full max-w-xl" />
        <Skeleton className="mt-2 h-4 w-3/4 max-w-xl" />
      </Container>
    )
  }

  if (notFound) {
    return (
      <Container className="py-16 sm:py-20">
        <EmptyState
          icon={SearchX}
          title="Service not found"
          description="This service doesn't exist or is no longer available."
          action={
            <Link
              to={paths.services}
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700"
            >
              <ArrowLeft className="size-4" aria-hidden="true" />
              Back to Services
            </Link>
          }
        />
      </Container>
    )
  }

  if (isError || !service) {
    return (
      <Container className="py-16 sm:py-20">
        <ErrorState
          title="Couldn't load this service"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      </Container>
    )
  }

  const price = formatMoney(service.price_from)

  return (
    <Container className="py-16 sm:py-20">
      <Link
        to={paths.services}
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600"
      >
        <ArrowLeft className="size-4" aria-hidden="true" />
        Back to Services
      </Link>

      <div className="mt-6 grid gap-10 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="flex size-14 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
            <Layers className="size-7" aria-hidden="true" />
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">{service.name}</h1>
            {service.category && <Badge variant="brand">{service.category}</Badge>}
          </div>
          {service.short_description && (
            <p className="mt-4 text-lg text-slate-600">{service.short_description}</p>
          )}
          {service.description && (
            <div className="mt-8 whitespace-pre-line text-base leading-relaxed text-slate-600">
              {service.description}
            </div>
          )}
        </div>

        <aside className="lg:col-span-1">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm font-medium text-slate-500">Starting from</p>
            <p className="mt-1 text-2xl font-bold text-slate-900">{price ?? 'Contact for pricing'}</p>
            <Link
              to={`${paths.requestQuote}?service=${service.id}`}
              className="mt-6 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-5 text-sm font-semibold text-white shadow-sm shadow-brand-900/10 transition-colors hover:bg-brand-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2"
            >
              Request a Quote
              <ArrowRight className="size-4" aria-hidden="true" />
            </Link>
            <p className="mt-3 text-center text-xs text-slate-400">No account needed to get started.</p>
          </div>
        </aside>
      </div>
    </Container>
  )
}
