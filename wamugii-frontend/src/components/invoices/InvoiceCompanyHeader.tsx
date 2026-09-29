import type { InvoiceCompanyBlock } from '@/api/settings'

export interface InvoiceCompanyHeaderProps {
  company: InvoiceCompanyBlock | null | undefined
  invoiceNumber: string
  /** Shown as "TAX INVOICE" when the invoice charges VAT. */
  isVat?: boolean
}

/**
 * The issuer block at the top of an invoice — what makes it read as a real
 * document rather than a screen. Rendered from company settings, so it is
 * empty until an admin fills them in; the whole block is skipped in that case
 * rather than printing a header of blanks.
 */
export function InvoiceCompanyHeader({
  company,
  invoiceNumber,
  isVat = false,
}: InvoiceCompanyHeaderProps) {
  if (!company) return null

  return (
    <div className="rounded-xl border border-slate-200 bg-panel p-6 shadow-[var(--shadow-card)] backdrop-blur-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-base font-bold text-slate-900">{company.company_name}</p>
          {/* Omitted entirely when no TIN is configured — never "TIN: None". */}
          {company.tin && (
            <p className="mt-1 text-sm font-medium text-slate-700">VAT Reg. No.: {company.tin}</p>
          )}
          <div className="mt-2 space-y-0.5 text-sm text-slate-500">
            {company.address && <p>{company.address}</p>}
            {company.phone && <p>{company.phone}</p>}
            {company.email && <p>{company.email}</p>}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            {isVat ? 'Tax Invoice' : 'Invoice'}
          </p>
          <p className="mt-1 text-sm font-semibold text-slate-900">{invoiceNumber}</p>
        </div>
      </div>
    </div>
  )
}
