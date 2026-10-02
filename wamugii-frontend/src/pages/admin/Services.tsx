import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Boxes } from 'lucide-react'
import { listAllServices } from '@/api/services'
import { usePageTitle } from '@/context/PageTitleContext'
import { paths } from '@/routes/paths'
import {
  Badge,
  EmptyState,
  ErrorState,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeaderCell,
  TableRow,
} from '@/components/ui'
import { formatMoney } from '@/utils/format'

/**
 * The services catalogue, for editing the public-facing copy and the quote
 * questions behind each service. Creating and deleting services stays with the
 * seed script — this screen is about maintaining the ones that exist.
 */
export function AdminServices() {
  usePageTitle('Services')
  const navigate = useNavigate()

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['services', 'admin', 'all'],
    queryFn: () => listAllServices({ include_inactive: true }),
  })

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">
        Edit each service&apos;s detail page copy and the questions its quote form asks.
      </p>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <ErrorState
          title="Couldn't load services"
          message="We had trouble reaching the server. Please try again."
          onRetry={() => refetch()}
        />
      ) : !data || data.length === 0 ? (
        <EmptyState
          icon={Boxes}
          title="No services yet"
          description="Run the service seed script to create the catalogue."
        />
      ) : (
        <Table>
          <TableHead>
            <TableHeaderCell>Service</TableHeaderCell>
            <TableHeaderCell>Category</TableHeaderCell>
            <TableHeaderCell>From</TableHeaderCell>
            <TableHeaderCell>Detail copy</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
          </TableHead>
          <TableBody>
            {data.map((service) => {
              const featureCount = service.features?.length ?? 0
              return (
                <TableRow
                  key={service.id}
                  clickable
                  onClick={() => navigate(paths.admin.serviceDetail(service.id))}
                >
                  <TableCell className="font-medium text-slate-900">{service.name}</TableCell>
                  <TableCell>{service.category ?? '—'}</TableCell>
                  <TableCell>{formatMoney(service.price_from) ?? '—'}</TableCell>
                  <TableCell>
                    {service.long_description || featureCount > 0 ? (
                      <span className="text-slate-600">
                        {service.long_description ? 'Write-up' : 'No write-up'}
                        {featureCount > 0 && ` · ${featureCount} feature(s)`}
                      </span>
                    ) : (
                      <span className="text-slate-400">Not set up</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {service.is_active ? (
                      <Badge variant="success">Published</Badge>
                    ) : (
                      <Badge variant="neutral">Hidden</Badge>
                    )}
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      )}
    </div>
  )
}
