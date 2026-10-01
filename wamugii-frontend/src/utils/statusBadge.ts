import type { BadgeVariant } from '@/components/ui/Badge'
import type { components } from '@/types/api'

type ProjectStatus = components['schemas']['ProjectStatus']
type ProjectPriority = components['schemas']['ProjectPriority']
type MilestoneStatus = components['schemas']['MilestoneStatus']
type QuoteStatus = components['schemas']['QuoteStatus']
type InvoiceStatus = components['schemas']['InvoiceStatus']
type HostingStatus = components['schemas']['HostingStatus']
type DomainStatus = components['schemas']['DomainStatus']
type TicketStatus = components['schemas']['TicketStatus']
type TicketPriority = components['schemas']['TicketPriority']
type Role = components['schemas']['Role']

export const projectStatusVariant: Record<ProjectStatus, BadgeVariant> = {
  PENDING: 'neutral',
  PLANNING: 'info',
  IN_PROGRESS: 'brand',
  ON_HOLD: 'warning',
  TESTING: 'info',
  CLIENT_REVIEW: 'warning',
  COMPLETED: 'success',
  CANCELLED: 'danger',
}

export const projectPriorityVariant: Record<ProjectPriority, BadgeVariant> = {
  LOW: 'neutral',
  MEDIUM: 'info',
  HIGH: 'warning',
  URGENT: 'danger',
}

export const milestoneStatusVariant: Record<MilestoneStatus, BadgeVariant> = {
  PENDING: 'neutral',
  IN_PROGRESS: 'brand',
  COMPLETED: 'success',
  ON_HOLD: 'warning',
  CANCELLED: 'danger',
}

export const quoteStatusVariant: Record<QuoteStatus, BadgeVariant> = {
  NEW: 'brand',
  REVIEWING: 'info',
  QUOTED: 'warning',
  ACCEPTED: 'success',
  REJECTED: 'danger',
  CANCELLED: 'neutral',
}

export const invoiceStatusVariant: Record<InvoiceStatus, BadgeVariant> = {
  DRAFT: 'neutral',
  SENT: 'info',
  PARTIALLY_PAID: 'warning',
  PAID: 'success',
  OVERDUE: 'danger',
  CANCELLED: 'neutral',
}

export const hostingStatusVariant: Record<HostingStatus, BadgeVariant> = {
  PENDING: 'neutral',
  ACTIVE: 'success',
  SUSPENDED: 'warning',
  EXPIRED: 'danger',
  CANCELLED: 'neutral',
}

export const domainStatusVariant: Record<DomainStatus, BadgeVariant> = {
  PENDING: 'neutral',
  ACTIVE: 'success',
  EXPIRED: 'danger',
  CANCELLED: 'neutral',
}

export const ticketStatusVariant: Record<TicketStatus, BadgeVariant> = {
  OPEN: 'brand',
  IN_PROGRESS: 'info',
  WAITING_ON_CLIENT: 'warning',
  RESOLVED: 'success',
  CLOSED: 'neutral',
}

/** Mirrors projectPriorityVariant -- same four levels, same reading. */
export const ticketPriorityVariant: Record<TicketPriority, BadgeVariant> = {
  LOW: 'neutral',
  MEDIUM: 'info',
  HIGH: 'warning',
  URGENT: 'danger',
}

export const roleVariant: Record<Role, BadgeVariant> = {
  ADMIN: 'brand',
  STAFF: 'info',
  CLIENT: 'neutral',
}
