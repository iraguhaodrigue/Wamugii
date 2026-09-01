import type { BadgeVariant } from '@/components/ui/Badge'
import type { components } from '@/types/api'

type ProjectStatus = components['schemas']['ProjectStatus']
type ProjectPriority = components['schemas']['ProjectPriority']
type MilestoneStatus = components['schemas']['MilestoneStatus']
type QuoteStatus = components['schemas']['QuoteStatus']
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

export const roleVariant: Record<Role, BadgeVariant> = {
  ADMIN: 'brand',
  STAFF: 'info',
  CLIENT: 'neutral',
}
