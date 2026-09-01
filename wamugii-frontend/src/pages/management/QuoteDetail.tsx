import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRightLeft, CheckCircle2, SearchX, Trash2 } from 'lucide-react'
import {
  convertQuoteToProject,
  deleteQuoteRequest,
  getQuoteRequest,
  updateQuoteRequest,
  type QuoteRequestRead,
  type QuoteStatus,
} from '@/api/quoteRequests'
import { listServices } from '@/api/services'
import { useUsersMap } from '@/hooks/useUsersMap'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Select, Skeleton, Textarea } from '@/components/ui'
import { formatDate, formatEnumLabel } from '@/utils/format'
import { quoteStatusVariant } from '@/utils/statusBadge'

const QUOTE_STATUSES: QuoteStatus[] = ['NEW', 'REVIEWING', 'QUOTED', 'ACCEPTED', 'REJECTED', 'CANCELLED']
const NO_CLIENT_MATCH_PREFIX = 'No client_id given and no user account matches'
const ALREADY_LINKED_PREFIX = 'This quote request is already linked'

export function QuoteDetail() {
  const { quoteId } = useParams<{ quoteId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const queryClient = useQueryClient()
  const { users } = useUsersMap()
  const { data: services } = useQuery({ queryKey: ['services', 'lookup'], queryFn: () => listServices() })
  const servicesMap = useMemo(() => new Map((services ?? []).map((s) => [s.id, s.name])), [services])

  const [status, setStatus] = useState<QuoteStatus | null>(null)
  const [adminNotes, setAdminNotes] = useState<string | null>(null)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [convertError, setConvertError] = useState<{ friendly: boolean; message: string } | null>(null)
  const [convertedProjectId, setConvertedProjectId] = useState<number | null>(null)
  const [showManualClientPicker, setShowManualClientPicker] = useState(false)
  const [manualClientId, setManualClientId] = useState('')

  const quoteQuery = useQuery<Awaited<ReturnType<typeof getQuoteRequest>>, ApiError>({
    queryKey: ['quote-requests', 'detail', quoteId],
    queryFn: () => getQuoteRequest(quoteId!),
    enabled: Boolean(quoteId),
    retry: (count, err) => err.status !== 404 && count < 1,
  })

  usePageTitle(quoteQuery.data?.project_title ?? 'Quote Request')

  const listPath = isAdmin ? paths.admin.quotes : paths.staff.quotes
  const projectDetailPath = isAdmin ? paths.admin.projectDetail : paths.staff.projectDetail

  const saveMutation = useMutation<QuoteRequestRead, ApiError>({
    mutationFn: () => updateQuoteRequest(quoteId!, { status: status ?? undefined, admin_notes: adminNotes ?? undefined }),
    onSuccess: (updated) => {
      queryClient.setQueryData(['quote-requests', 'detail', quoteId], updated)
      queryClient.invalidateQueries({ queryKey: ['quote-requests'] })
      setStatus(null)
      setAdminNotes(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteQuoteRequest(quoteId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quote-requests'] })
      navigate(listPath)
    },
  })

  const convertMutation = useMutation({
    mutationFn: (clientId?: number) => convertQuoteToProject(quoteId!, clientId),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setConvertedProjectId(project.id)
      setConvertError(null)
      setShowManualClientPicker(false)
    },
    onError: (err: ApiError) => {
      if (err.status === 422 && err.message.startsWith(NO_CLIENT_MATCH_PREFIX)) {
        setConvertError({
          friendly: true,
          message: "No client account matches this quote's email — the client must register first.",
        })
        setShowManualClientPicker(true)
        return
      }
      if (err.status === 409 && err.message.startsWith(ALREADY_LINKED_PREFIX)) {
        setConvertError({ friendly: true, message: 'This quote has already been converted into a project.' })
        return
      }
      setConvertError({ friendly: false, message: err.message })
    },
  })

  if (quoteQuery.isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-9 w-1/2" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
    )
  }

  const notFound = quoteQuery.isError && quoteQuery.error.status === 404
  if (notFound) {
    return (
      <EmptyState
        icon={SearchX}
        title="Quote request not found"
        description="This quote request doesn't exist."
        action={
          <Link to={listPath} className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-600 hover:text-brand-700">
            <ArrowLeft className="size-4" aria-hidden="true" />
            Back to Quote Requests
          </Link>
        }
      />
    )
  }

  if (quoteQuery.isError || !quoteQuery.data) {
    return (
      <ErrorState
        title="Couldn't load this quote request"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => quoteQuery.refetch()}
      />
    )
  }

  const quote = quoteQuery.data
  const currentStatus = status ?? quote.status
  const currentNotes = adminNotes ?? (quote.admin_notes ?? '')
  const hasChanges = (status !== null && status !== quote.status) || (adminNotes !== null && adminNotes !== (quote.admin_notes ?? ''))
  const activeClients = users.filter((u) => u.role === 'CLIENT' && u.is_active)

  return (
    <div className="space-y-6">
      <div>
        <Link to={listPath} className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 hover:text-brand-600">
          <ArrowLeft className="size-4" aria-hidden="true" />
          Back to Quote Requests
        </Link>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">{quote.project_title}</h1>
            <Badge variant={quoteStatusVariant[quote.status]}>{formatEnumLabel(quote.status)}</Badge>
          </div>
          {isAdmin && (
            <Button size="sm" variant="danger" leftIcon={<Trash2 className="size-4" />} onClick={() => setIsDeleteOpen(true)}>
              Delete
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Project details</h2>
            <dl className="mt-3 space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Service</dt>
                <dd className="font-medium text-slate-900">
                  {quote.service_id ? (servicesMap.get(quote.service_id) ?? `#${quote.service_id}`) : 'Not specified'}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Description</dt>
                <dd className="mt-1 whitespace-pre-line text-slate-700">{quote.project_description}</dd>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <dt className="text-slate-500">Budget range</dt>
                  <dd className="font-medium text-slate-900">{quote.budget_range ?? 'Not specified'}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Preferred deadline</dt>
                  <dd className="font-medium text-slate-900">{quote.preferred_deadline ?? 'Not specified'}</dd>
                </div>
              </div>
            </dl>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Status &amp; internal notes</h2>
            <div className="mt-4 space-y-4">
              <Select
                label="Status"
                options={QUOTE_STATUSES.map((s) => ({ value: s, label: formatEnumLabel(s) }))}
                value={currentStatus}
                onChange={(e) => setStatus(e.target.value as QuoteStatus)}
              />
              <Textarea
                label="Admin notes"
                rows={4}
                hint="Internal only — never shown to the client"
                value={currentNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
              />
              {saveMutation.isError && (
                <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                  {saveMutation.error.message}
                </p>
              )}
              <div className="flex justify-end">
                <Button size="sm" disabled={!hasChanges} isLoading={saveMutation.isPending} onClick={() => saveMutation.mutate()}>
                  Save Changes
                </Button>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
              <ArrowRightLeft className="size-4" aria-hidden="true" />
              Convert to Project
            </h2>

            {convertedProjectId ? (
              <div className="mt-4 flex items-center gap-3 rounded-lg bg-green-50 px-4 py-3 text-sm text-green-800">
                <CheckCircle2 className="size-5 shrink-0" aria-hidden="true" />
                <span>
                  Converted successfully.{' '}
                  <Link to={projectDetailPath(convertedProjectId)} className="font-semibold underline">
                    View the new project
                  </Link>
                </span>
              </div>
            ) : quote.status !== 'ACCEPTED' ? (
              <p className="mt-3 text-sm text-slate-500">
                Only quotes with status <span className="font-medium">Accepted</span> can be converted into a project.
              </p>
            ) : (
              <div className="mt-4 space-y-3">
                <p className="text-sm text-slate-500">
                  Creates a project for this quote. We'll try to match an existing client account by email first.
                </p>
                {convertError && (
                  <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                    {convertError.message}
                  </p>
                )}
                {!showManualClientPicker ? (
                  <Button
                    size="sm"
                    isLoading={convertMutation.isPending}
                    onClick={() => convertMutation.mutate(undefined)}
                  >
                    Convert to Project
                  </Button>
                ) : (
                  <div className="space-y-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
                    <p className="text-sm text-amber-800">
                      You can assign this quote to an existing client account manually instead.
                    </p>
                    <Select
                      label="Assign to client"
                      options={activeClients.map((c) => ({ value: String(c.id), label: `${c.full_name} (${c.email})` }))}
                      placeholder="Select a client"
                      value={manualClientId}
                      onChange={(e) => setManualClientId(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        disabled={!manualClientId}
                        isLoading={convertMutation.isPending}
                        onClick={() => convertMutation.mutate(Number(manualClientId))}
                      >
                        Assign &amp; Convert
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setShowManualClientPicker(false)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4 rounded-xl border border-slate-200 bg-panel p-6 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Contact</h2>
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">Name</dt>
              <dd className="font-medium text-slate-900">{quote.full_name}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Email</dt>
              <dd className="font-medium text-slate-900">{quote.email}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Phone</dt>
              <dd className="font-medium text-slate-900">{quote.phone}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Company</dt>
              <dd className="font-medium text-slate-900">{quote.company_name ?? 'Not specified'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Submitted</dt>
              <dd className="font-medium text-slate-900">{formatDate(quote.created_at)}</dd>
            </div>
          </dl>
        </div>
      </div>

      <ConfirmDialog
        isOpen={isDeleteOpen}
        onClose={() => setIsDeleteOpen(false)}
        onConfirm={() => deleteMutation.mutate()}
        title="Delete this quote request?"
        description="This soft-deletes the quote request. It will no longer appear in the list."
        confirmLabel="Delete"
        isDanger
        isLoading={deleteMutation.isPending}
      />
    </div>
  )
}
