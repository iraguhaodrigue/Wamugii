import { useQuery } from '@tanstack/react-query'
import {
  Boxes,
  Clock,
  FolderKanban,
  HeadphonesIcon,
  Receipt,
  Server,
  ShoppingBag,
  Sparkles,
  Users,
  Wallet,
} from 'lucide-react'
import { getAdminDashboard } from '@/api/adminDashboard'
import { useAuth } from '@/context/AuthContext'
import { usePageTitle } from '@/context/PageTitleContext'
import { Avatar, ErrorState, Skeleton, StatCard } from '@/components/ui'
import { formatMoney } from '@/utils/format'

const comingSoonTiles = [
  { label: 'Hosting', icon: Server },
  { label: 'Store', icon: ShoppingBag },
  { label: 'Support', icon: HeadphonesIcon },
]

export function AdminDashboard() {
  usePageTitle('Dashboard')
  const { user } = useAuth()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['admin', 'dashboard'],
    queryFn: getAdminDashboard,
  })

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-32 rounded-xl" />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <ErrorState
        title="Couldn't load the dashboard"
        message="We had trouble reaching the server. Please try again."
        onRetry={() => refetch()}
      />
    )
  }

  return (
    <div className="space-y-10">
      <div className="relative overflow-hidden rounded-xl bg-brand-700 p-6 shadow-lg shadow-brand-950/30 sm:p-8">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.15]"
          style={{
            backgroundImage: 'radial-gradient(circle at 1px 1px, white 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }}
          aria-hidden="true"
        />
        <div className="relative flex items-center gap-4">
          {user && <Avatar name={user.full_name} size="lg" className="ring-2 ring-white/30" />}
          <div>
            <p className="flex items-center gap-1.5 text-sm font-medium text-brand-100">
              <Sparkles className="size-4" aria-hidden="true" />
              Welcome back
            </p>
            <h2 className="mt-0.5 text-2xl font-bold text-white">{user?.full_name.split(' ')[0]}</h2>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Platform overview</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard icon={Users} label="Total Users" value={data.users.total} accent="brand" />
          <StatCard
            icon={Boxes}
            label="Active Services"
            value={`${data.services.active}/${data.services.total}`}
            accent="accent"
          />
          <StatCard
            icon={FolderKanban}
            label="Active Projects"
            value={`${data.projects.active}/${data.projects.total}`}
            accent="success"
          />
          <StatCard icon={Clock} label="Pending Quotes" value={data.quotes.pending} accent="warning" />
          <StatCard
            icon={Wallet}
            label="Outstanding Payments"
            value={formatMoney(data.invoices.outstanding) ?? '—'}
            accent="brand"
          />
          <StatCard
            icon={Receipt}
            label="Unpaid Invoices"
            value={data.invoices.pending}
            accent="accent"
          />
        </div>
        <p className="mt-3 text-xs text-slate-400">
          Users: {data.users.clients} clients · {data.users.staff} staff · {data.users.admins} admins
        </p>
      </div>

      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Coming soon</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {comingSoonTiles.map(({ label, icon: Icon }) => (
            <div
              key={label}
              className="flex items-center gap-4 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-slate-400"
            >
              <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-slate-200/60">
                <Icon className="size-5" aria-hidden="true" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className="text-xs text-slate-400">Coming soon</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
