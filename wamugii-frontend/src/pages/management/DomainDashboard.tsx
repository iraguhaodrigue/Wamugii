import { useState, type FormEvent, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import {
  AlertTriangle,
  CalendarClock,
  CheckCircle2,
  Clock,
  ExternalLink,
  Globe,
  List,
  Pencil,
  Plus,
  Search,
  Tag,
  Wallet,
} from 'lucide-react'
import {
  createExtension,
  getDomainDashboard,
  listAllExtensions,
  updateDomain,
  updateExtension,
  type DashboardDomainRow,
  type DomainExtension,
} from '@/api/domains'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import type { ApiError } from '@/lib/apiClient'
import { paths } from '@/routes/paths'
import { Button, ErrorState, Input, Modal, Skeleton, StatCard } from '@/components/ui'
import { formatDate, formatMoney, formatRelativeTime } from '@/utils/format'
import { cn } from '@/utils/cn'

/**
 * The domain dashboard for admin and staff: new online requests to register,
 * renewals coming up, what the domains are worth, what visitors search for,
 * and (admin only) the price list.
 */
export function DomainDashboard() {
  usePageTitle('Domains')
  const { user } = useAuth()
  const isAdmin = user?.role === 'ADMIN'
  const base = isAdmin ? paths.admin : paths.staff
  const navigate = useNavigate()
  const [registering, setRegistering] = useState<DashboardDomainRow | null>(null)

  const dash = useQuery({ queryKey: ['domains', 'dashboard'], queryFn: getDomainDashboard })

  if (dash.isError)
    return (
      <ErrorState
        title="Couldn't load the domain dashboard"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => dash.refetch()}
      />
    )

  const d = dash.data
  const overdue = d?.expiring.filter((e) => (e.days_left ?? 0) < 0).length ?? 0
  const maxExt = Math.max(1, ...(d?.by_extension.map((e) => e.count) ?? [1]))

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Domains</h1>
          <p className="mt-1 text-sm text-slate-600">Requests to register, renewals, value and what people search for.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link
            to={paths.domains}
            target="_blank"
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-300 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-100"
          >
            <Search className="size-4" aria-hidden="true" /> Search page <ExternalLink className="size-3.5" aria-hidden="true" />
          </Link>
          <Link
            to={base.domainsAll}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)] px-4 text-sm font-semibold text-white transition-[filter] hover:brightness-110"
          >
            <List className="size-4" aria-hidden="true" /> All domains
          </Link>
        </div>
      </div>

      {!d ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard icon={Globe} label="Active domains" value={d.counts.ACTIVE ?? 0} accent="brand" />
            <StatCard icon={Clock} label="New requests" value={d.counts.PENDING ?? 0} accent="accent" />
            <StatCard icon={CalendarClock} label="Renewals due" value={d.expiring.length} accent="warning" />
            <StatCard icon={Wallet} label="Yearly value" value={formatMoney(d.yearly_value) ?? '—'} accent="success" />
          </div>

          <Panel
            title="New requests"
            subtitle="Clients asked for these from the search page. Register each one, then send the invoice."
          >
            {d.pending_requests.length === 0 ? (
              <Empty text="No requests waiting. New ones appear here and in your notifications." />
            ) : (
              <ul className="divide-y divide-slate-200">
                {d.pending_requests.map((r) => (
                  <li key={r.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                    <button type="button" className="min-w-0 text-left" onClick={() => navigate(base.domainDetail(r.id))}>
                      <p className="font-semibold text-slate-900 hover:underline">{r.domain_name}</p>
                      <p className="text-sm text-slate-600">
                        {r.client_name} · {formatMoney(r.total_fee)} · requested {formatRelativeTime(r.created_at)}
                      </p>
                    </button>
                    <Button size="sm" onClick={() => setRegistering(r)} leftIcon={<CheckCircle2 className="size-4" />}>
                      Mark registered
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </Panel>

          <Panel
            title="Renewals due"
            subtitle={overdue ? `${overdue} already past the expiry date — renew these first.` : 'Active domains that expire within 90 days.'}
          >
            {d.expiring.length === 0 ? (
              <Empty text="Nothing expires in the next 90 days." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full min-w-[34rem] text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-600">
                      <th scope="col" className="py-2 pr-3 font-semibold">Domain</th>
                      <th scope="col" className="py-2 pr-3 font-semibold">Client</th>
                      <th scope="col" className="py-2 pr-3 font-semibold">Expires</th>
                      <th scope="col" className="py-2 pr-3 font-semibold">Auto-renew</th>
                      <th scope="col" className="py-2 text-right font-semibold">Renewal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.expiring.map((r) => (
                      <tr
                        key={r.id}
                        className="cursor-pointer border-b border-slate-200 last:border-0 hover:bg-slate-50"
                        onClick={() => navigate(base.domainDetail(r.id))}
                      >
                        <td className="py-2.5 pr-3 font-medium text-slate-900">{r.domain_name}</td>
                        <td className="py-2.5 pr-3 text-slate-700">{r.client_name}</td>
                        <td className="py-2.5 pr-3">
                          <DaysLeft row={r} />
                        </td>
                        <td className="py-2.5 pr-3 text-slate-700">{r.auto_renew ? 'Yes' : 'No'}</td>
                        <td className="py-2.5 text-right text-slate-700">{formatMoney(r.total_fee)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>

          <div className="grid gap-6 lg:grid-cols-2">
            <Panel title="Domains by extension" subtitle="Active and requested domains.">
              {d.by_extension.length === 0 ? (
                <Empty text="No domains yet." />
              ) : (
                <ul className="space-y-3">
                  {d.by_extension.map((e) => (
                    <li key={e.extension} className="grid grid-cols-[4.5rem_1fr_2rem] items-center gap-3 text-sm">
                      <span className="font-semibold text-slate-900">{e.extension}</span>
                      <span className="h-2.5 rounded-full bg-slate-200">
                        <span
                          className="block h-full rounded-full bg-gradient-to-r from-[var(--color-brand-solid)] to-[var(--color-accent-solid)]"
                          style={{ width: `${(e.count / maxExt) * 100}%` }}
                        />
                      </span>
                      <span className="text-right text-slate-700">{e.count}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Panel>

            <Panel
              title="What people search for"
              subtitle={`${d.searches_7_days} searches this week · ${d.searches_30_days} in 30 days${
                d.available_share !== null && d.available_share !== undefined
                  ? ` · ${Math.round(d.available_share * 100)}% found a free name`
                  : ''
              }`}
            >
              {d.top_searches.length === 0 ? (
                <Empty text="No searches yet. Share the search page with customers." />
              ) : (
                <ol className="space-y-2">
                  {d.top_searches.map((s, i) => (
                    <li key={s.name} className="flex items-center justify-between gap-3 text-sm">
                      <span className="min-w-0 truncate text-slate-900">
                        <span className="mr-2 text-slate-500">{i + 1}.</span>
                        {s.name}
                      </span>
                      <span className="shrink-0 text-slate-600">
                        {s.searches}× · {formatRelativeTime(s.last_searched)}
                      </span>
                    </li>
                  ))}
                </ol>
              )}
              <p className="mt-4 text-xs text-slate-500">
                Popular names are sales leads: a visitor wanted this name but may not have ordered yet.
              </p>
            </Panel>
          </div>

          {isAdmin && <PriceList />}
        </>
      )}

      {registering && <RegisterModal row={registering} onClose={() => setRegistering(null)} />}
    </div>
  )
}

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-panel p-5 shadow-[var(--shadow-card)] sm:p-6">
      <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
      {subtitle && <p className="mt-1 text-sm text-slate-600">{subtitle}</p>}
      <div className="mt-4">{children}</div>
    </section>
  )
}

function Empty({ text }: { text: string }) {
  return <p className="rounded-xl border border-dashed border-slate-300 px-4 py-6 text-center text-sm text-slate-600">{text}</p>
}

function DaysLeft({ row }: { row: DashboardDomainRow }) {
  const days = row.days_left ?? 0
  const label = days < 0 ? `${-days} day${days === -1 ? '' : 's'} overdue` : days === 0 ? 'today' : `in ${days} days`
  return (
    <span className="flex flex-wrap items-center gap-2">
      <span className="text-slate-700">{formatDate(row.expires_at)}</span>
      <span
        className={cn(
          'rounded-full px-2 py-0.5 text-xs font-semibold',
          days < 0 ? 'bg-red-100 text-red-800' : days <= 30 ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700',
        )}
      >
        {days < 0 && <AlertTriangle className="-mt-0.5 mr-1 inline size-3" aria-hidden="true" />}
        {label}
      </span>
    </span>
  )
}

function addYears(isoDate: string, years: number): string {
  const [y = 1970, m = 1, day = 1] = isoDate.split('-').map(Number)
  const result = new Date(Date.UTC(y + years, m - 1, day))
  return result.toISOString().slice(0, 10)
}

function RegisterModal({ row, onClose }: { row: DashboardDomainRow; onClose: () => void }) {
  const today = new Date().toISOString().slice(0, 10)
  const [registrar, setRegistrar] = useState(row.domain_name.endsWith('.rw') ? '' : 'Namecheap')
  const [registered, setRegistered] = useState(today)
  const [years, setYears] = useState(1)
  const [nameservers, setNameservers] = useState('')
  const queryClient = useQueryClient()
  const save = useMutation({
    mutationFn: () =>
      updateDomain(row.id, {
        status: 'ACTIVE',
        registrar: registrar.trim() || 'Registrar not set',
        registered_date: registered,
        expires_at: addYears(registered, years),
        nameservers: nameservers.trim() || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
      onClose()
    },
  })
  const error = save.error as ApiError | null

  function submit(e: FormEvent) {
    e.preventDefault()
    save.mutate()
  }

  return (
    <Modal isOpen onClose={onClose} title={`Mark ${row.domain_name} as registered`}>
      <form onSubmit={submit} className="space-y-4">
        <p className="text-sm text-slate-600">
          Register it first with the registrar, then record it here. {row.client_name} gets a notification that the domain
          is active.
        </p>
        <Input label="Registrar" value={registrar} onChange={(e) => setRegistrar(e.target.value)} placeholder="e.g. the .rw registrar you used" required />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input label="Registered on" type="date" value={registered} onChange={(e) => setRegistered(e.target.value)} required />
          <label className="block text-sm">
            <span className="font-medium text-slate-700">Registered for</span>
            <select
              value={years}
              onChange={(e) => setYears(Number(e.target.value))}
              className="mt-1.5 h-10 w-full rounded-lg border border-slate-300 bg-transparent px-3 text-sm text-slate-900"
            >
              {[1, 2, 3, 4, 5].map((y) => (
                <option key={y} value={y}>
                  {y} year{y > 1 ? 's' : ''}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="text-sm text-slate-600">Expires on {formatDate(addYears(registered, years))}</p>
        <Input label="Nameservers (optional)" value={nameservers} onChange={(e) => setNameservers(e.target.value)} placeholder="ns1.example.com, ns2.example.com" />
        {error && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error.message}
          </p>
        )}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={save.isPending}>
            Save — domain is active
          </Button>
        </div>
      </form>
    </Modal>
  )
}

function PriceList() {
  const queryClient = useQueryClient()
  const list = useQuery({ queryKey: ['domains', 'extensions', 'manage'], queryFn: listAllExtensions })
  const [editing, setEditing] = useState<DomainExtension | 'new' | null>(null)
  const toggle = useMutation({
    mutationFn: (e: DomainExtension) => updateExtension(e.id, { is_active: !e.is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['domains'] }),
  })

  return (
    <Panel title="Price list" subtitle="What clients pay per year = your registrar cost + your margin. Only active extensions appear in search.">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[36rem] text-sm">
          <thead>
            <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-600">
              <th scope="col" className="py-2 pr-3 font-semibold">Extension</th>
              <th scope="col" className="py-2 pr-3 text-right font-semibold">Cost</th>
              <th scope="col" className="py-2 pr-3 text-right font-semibold">Margin</th>
              <th scope="col" className="py-2 pr-3 text-right font-semibold">Client price</th>
              <th scope="col" className="py-2 pr-3 font-semibold">In search</th>
              <th scope="col" className="py-2 text-right font-semibold">
                <span className="sr-only">Edit</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {(list.data ?? []).map((e) => (
              <tr key={e.id} className={cn('border-b border-slate-200 last:border-0', e.is_active ? 'text-slate-700' : 'text-slate-500')}>
                <td className="py-2.5 pr-3 font-semibold text-slate-900">{e.extension}</td>
                <td className="py-2.5 pr-3 text-right">{formatMoney(e.cost_price)}</td>
                <td className="py-2.5 pr-3 text-right">{formatMoney(e.margin)}</td>
                <td className="py-2.5 pr-3 text-right font-semibold text-slate-900">{formatMoney(e.client_price)}</td>
                <td className="py-2.5 pr-3">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={e.is_active}
                    aria-label={`Show ${e.extension} in search`}
                    onClick={() => toggle.mutate(e)}
                    className={cn(
                      'relative h-6 w-11 rounded-full transition-colors',
                      e.is_active ? 'bg-emerald-600' : 'bg-slate-300',
                    )}
                  >
                    <span
                      className={cn(
                        'absolute left-0.5 top-0.5 size-5 rounded-full bg-white shadow transition-transform',
                        e.is_active ? 'translate-x-5' : 'translate-x-0',
                      )}
                    />
                  </button>
                </td>
                <td className="py-2.5 text-right">
                  <Button size="sm" variant="ghost" onClick={() => setEditing(e)} leftIcon={<Pencil className="size-3.5" />}>
                    Edit
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <p className="flex items-center gap-2 text-xs text-slate-500">
          <Tag className="size-3.5" aria-hidden="true" /> Starting prices are placeholders — enter your real registrar costs.
        </p>
        <Button size="sm" variant="outline" onClick={() => setEditing('new')} leftIcon={<Plus className="size-4" />}>
          Add extension
        </Button>
      </div>
      {editing && <ExtensionModal ext={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
    </Panel>
  )
}

function ExtensionModal({ ext, onClose }: { ext: DomainExtension | null; onClose: () => void }) {
  const [extension, setExtension] = useState(ext?.extension ?? '')
  const [cost, setCost] = useState(ext ? String(Number(ext.cost_price)) : '')
  const [margin, setMargin] = useState(ext ? String(Number(ext.margin)) : '5000')
  const [order, setOrder] = useState(String(ext?.display_order ?? 10))
  const queryClient = useQueryClient()
  const save = useMutation({
    mutationFn: () =>
      ext
        ? updateExtension(ext.id, { cost_price: cost, margin, display_order: Number(order) })
        : createExtension({ extension, cost_price: cost, margin, display_order: Number(order), is_active: true }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['domains'] })
      onClose()
    },
  })
  const error = save.error as ApiError | null
  const total = Number(cost || 0) + Number(margin || 0)

  return (
    <Modal isOpen onClose={onClose} title={ext ? `Edit ${ext.extension}` : 'Add an extension'} size="sm">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          save.mutate()
        }}
        className="space-y-4"
      >
        {!ext && (
          <Input label="Extension" value={extension} onChange={(e) => setExtension(e.target.value)} placeholder=".co.rw" required />
        )}
        <Input label="Registrar cost per year (RWF)" type="number" min={0} value={cost} onChange={(e) => setCost(e.target.value)} required />
        <Input label="Your margin per year (RWF)" type="number" min={0} value={margin} onChange={(e) => setMargin(e.target.value)} required />
        <Input label="Order in lists" type="number" value={order} onChange={(e) => setOrder(e.target.value)} hint="Lower numbers show first" />
        <p className="text-sm text-slate-600">
          Client pays <strong className="text-slate-900">{formatMoney(String(total))}</strong> per year.
        </p>
        {error && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error.message}
          </p>
        )}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={save.isPending}>
            Save
          </Button>
        </div>
      </form>
    </Modal>
  )
}
