import { apiClient } from '@/lib/apiClient'
import type { components } from '@/types/api'

export type SupportTicket = components['schemas']['SupportTicketRead']
export type SupportTicketListItem = components['schemas']['SupportTicketListItem']
export type SupportTicketCreate = components['schemas']['SupportTicketCreate']
export type SupportTicketAdminCreate = components['schemas']['SupportTicketAdminCreate']
export type SupportTicketUpdate = components['schemas']['SupportTicketUpdate']
export type TicketMessage = components['schemas']['TicketMessageRead']
export type TicketMessageCreate = components['schemas']['TicketMessageCreate']
export type TicketStatus = components['schemas']['TicketStatus']
export type TicketPriority = components['schemas']['TicketPriority']
export type TicketCategory = components['schemas']['TicketCategory']

export type ClientTicket = components['schemas']['ClientTicketDetail']
export type ClientTicketListItem = components['schemas']['ClientTicketListItem']
export type ClientTicketMessage = components['schemas']['ClientTicketMessageRead']

export const TICKET_STATUSES: TicketStatus[] = [
  'OPEN',
  'IN_PROGRESS',
  'WAITING_ON_CLIENT',
  'RESOLVED',
  'CLOSED',
]

export const TICKET_PRIORITIES: TicketPriority[] = ['LOW', 'MEDIUM', 'HIGH', 'URGENT']

export const TICKET_CATEGORIES: TicketCategory[] = [
  'GENERAL',
  'BILLING',
  'TECHNICAL',
  'PROJECT_CHANGE',
  'HOSTING',
  'OTHER',
]

/**
 * Statuses that email the client when set — worth a confirmation step so staff
 * don't send "resolved" by a mis-click on a dropdown.
 */
export const NOTIFYING_TICKET_STATUSES: TicketStatus[] = [
  'RESOLVED',
  'CLOSED',
  'WAITING_ON_CLIENT',
]

// --- staff ------------------------------------------------------------------

export interface ListTicketsParams {
  status?: TicketStatus
  priority?: TicketPriority
  category?: TicketCategory
  client_id?: number
  assigned_to?: number
  search?: string
  include_inactive?: boolean
  limit?: number
  offset?: number
}

export async function listTickets(
  params: ListTicketsParams = {},
): Promise<SupportTicketListItem[]> {
  const { data } = await apiClient.get<SupportTicketListItem[]>('/tickets', { params })
  return data
}

export async function getTicket(ticketId: number | string): Promise<SupportTicket> {
  const { data } = await apiClient.get<SupportTicket>(`/tickets/${ticketId}`)
  return data
}

export async function createTicketForClient(
  payload: SupportTicketAdminCreate,
): Promise<SupportTicket> {
  const { data } = await apiClient.post<SupportTicket>('/tickets', payload)
  return data
}

export async function updateTicket(
  ticketId: number | string,
  payload: SupportTicketUpdate,
): Promise<SupportTicket> {
  const { data } = await apiClient.patch<SupportTicket>(`/tickets/${ticketId}`, payload)
  return data
}

/** `is_internal_note: true` is staff-only — never emailed, never shown to the client. */
export async function addStaffMessage(
  ticketId: number | string,
  payload: TicketMessageCreate,
): Promise<TicketMessage> {
  const { data } = await apiClient.post<TicketMessage>(`/tickets/${ticketId}/messages`, payload)
  return data
}

export async function deactivateTicket(ticketId: number | string): Promise<SupportTicket> {
  const { data } = await apiClient.delete<SupportTicket>(`/tickets/${ticketId}`)
  return data
}

// --- client portal ----------------------------------------------------------

export async function createClientTicket(payload: SupportTicketCreate): Promise<ClientTicket> {
  const { data } = await apiClient.post<ClientTicket>('/client/tickets', payload)
  return data
}

export async function listClientTickets(
  params: { status?: TicketStatus; limit?: number; offset?: number } = {},
): Promise<ClientTicketListItem[]> {
  const { data } = await apiClient.get<ClientTicketListItem[]>('/client/tickets', { params })
  return data
}

export async function getClientTicket(ticketId: number | string): Promise<ClientTicket> {
  const { data } = await apiClient.get<ClientTicket>(`/client/tickets/${ticketId}`)
  return data
}

export async function addClientMessage(
  ticketId: number | string,
  message: string,
): Promise<ClientTicketMessage> {
  // `is_internal_note` is deliberately not sent: the backend ignores it on this
  // endpoint anyway, and omitting it keeps the intent obvious.
  const { data } = await apiClient.post<ClientTicketMessage>(
    `/client/tickets/${ticketId}/messages`,
    { message },
  )
  return data
}
