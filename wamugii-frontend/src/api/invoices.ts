import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type InvoiceRead = components['schemas']['InvoiceRead']
export type InvoiceListItem = components['schemas']['InvoiceListItem']
export type InvoiceCreate = components['schemas']['InvoiceCreate']
export type InvoiceUpdate = components['schemas']['InvoiceUpdate']
export type InvoiceItemCreate = components['schemas']['InvoiceItemCreate']
export type InvoiceItemRead = components['schemas']['InvoiceItemRead']
export type InvoiceStatus = components['schemas']['InvoiceStatus']
export type PaymentCreate = components['schemas']['PaymentCreate']
export type PaymentRead = components['schemas']['PaymentRead']
export type PaymentMethod = components['schemas']['PaymentMethod']

export type ClientInvoiceListItem = components['schemas']['ClientInvoiceListItem']
export type ClientInvoiceDetail = components['schemas']['ClientInvoiceDetail']

/**
 * Only these three are user-settable. PAID / PARTIALLY_PAID / OVERDUE are
 * derived server-side from the amounts and the due date — offering them in a
 * form would let the user assert a state the money contradicts (the backend
 * rejects it with 422 anyway).
 */
export const SETTABLE_INVOICE_STATUSES: InvoiceStatus[] = ['DRAFT', 'SENT', 'CANCELLED']

export const PAYMENT_METHODS: PaymentMethod[] = ['MOBILE_MONEY', 'BANK_TRANSFER', 'CASH', 'OTHER']

/**
 * Rwanda's standard VAT rate. WAMUGII is VAT-registered with RRA, so invoices
 * carry this as a formal rate rather than a hand-typed amount. Sent as a
 * decimal string like every other money/rate field; the server derives the
 * actual tax amount from it and never trusts a client-sent tax figure.
 */
export const VAT_RATE = '18'

/** True when the invoice charges VAT at a formal rate rather than a manual amount. */
export function hasVatRate(taxRate: string | null | undefined): boolean {
  return taxRate !== null && taxRate !== undefined && Number(taxRate) > 0
}

/** "18.00" -> "18" for display in labels like "VAT (18%)". */
export function formatRateLabel(taxRate: string): string {
  const numeric = Number(taxRate)
  return Number.isFinite(numeric) ? String(numeric) : taxRate
}

/** Statuses the backend locks against edits (notes excepted) — see 409 handling. */
export function isInvoiceLocked(status: InvoiceStatus): boolean {
  return status === 'PAID' || status === 'CANCELLED'
}

export interface ListInvoicesParams {
  status?: InvoiceStatus
  client_id?: number
  project_id?: number
  search?: string
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listInvoices(params: ListInvoicesParams = {}): Promise<InvoiceListItem[]> {
  const { data } = await apiClient.get<InvoiceListItem[]>('/invoices', { params })
  return data
}

export async function getInvoice(invoiceId: number | string): Promise<InvoiceRead> {
  const { data } = await apiClient.get<InvoiceRead>(`/invoices/${invoiceId}`)
  return data
}

export async function createInvoice(payload: InvoiceCreate): Promise<InvoiceRead> {
  const { data } = await apiClient.post<InvoiceRead>('/invoices', payload)
  return data
}

export async function updateInvoice(
  invoiceId: number | string,
  payload: InvoiceUpdate,
): Promise<InvoiceRead> {
  const { data } = await apiClient.patch<InvoiceRead>(`/invoices/${invoiceId}`, payload)
  return data
}

export async function deactivateInvoice(invoiceId: number | string): Promise<InvoiceRead> {
  const { data } = await apiClient.delete<InvoiceRead>(`/invoices/${invoiceId}`)
  return data
}

export async function recordPayment(
  invoiceId: number | string,
  payload: PaymentCreate,
): Promise<PaymentRead> {
  const { data } = await apiClient.post<PaymentRead>(`/invoices/${invoiceId}/payments`, payload)
  return data
}

export async function listInvoicePayments(invoiceId: number | string): Promise<PaymentRead[]> {
  const { data } = await apiClient.get<PaymentRead[]>(`/invoices/${invoiceId}/payments`)
  return data
}

// --- client portal (scoped to the authenticated client by the backend) ------

export interface ListClientInvoicesParams {
  status?: InvoiceStatus
  limit?: number
  offset?: number
}

export async function listClientInvoices(
  params: ListClientInvoicesParams = {},
): Promise<ClientInvoiceListItem[]> {
  const { data } = await apiClient.get<ClientInvoiceListItem[]>('/client/invoices', { params })
  return data
}

export async function getClientInvoice(invoiceId: number | string): Promise<ClientInvoiceDetail> {
  const { data } = await apiClient.get<ClientInvoiceDetail>(`/client/invoices/${invoiceId}`)
  return data
}
