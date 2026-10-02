import type { components } from '@/types/api'

type Role = components['schemas']['Role']

export const paths = {
  home: '/',
  services: '/services',
  hosting: '/hosting',
  serviceDetail: (id: string | number) => `/services/${id}`,
  requestQuote: '/request-quote',
  login: '/login',
  register: '/register',
  forgotPassword: '/forgot-password',
  /** Public self-registration for project collaborators. */
  joinTeam: '/join',
  /** Shown instead of a dashboard while an account is awaiting approval. */
  pendingApproval: '/pending-approval',
  resetPassword: '/reset-password',
  client: {
    dashboard: '/client/dashboard',
    projects: '/client/projects',
    projectDetail: (id: string | number) => `/client/projects/${id}`,
    invoices: '/client/invoices',
    invoiceDetail: (id: string | number) => `/client/invoices/${id}`,
    hosting: '/client/hosting',
    hostingDetail: (id: string | number) => `/client/hosting/${id}`,
    domains: '/client/domains',
    domainDetail: (id: string | number) => `/client/domains/${id}`,
    quoteDetail: (id: string | number) => `/client/quotes/${id}`,
    tickets: '/client/support',
    ticketDetail: (id: string | number) => `/client/support/${id}`,
  },
  staff: {
    overview: '/staff',
    projects: '/staff/projects',
    projectDetail: (id: string | number) => `/staff/projects/${id}`,
    quotes: '/staff/quotes',
    quoteDetail: (id: string | number) => `/staff/quotes/${id}`,
    invoices: '/staff/invoices',
    invoiceDetail: (id: string | number) => `/staff/invoices/${id}`,
    hostingAccounts: '/staff/hosting/accounts',
    hostingAccountDetail: (id: string | number) => `/staff/hosting/accounts/${id}`,
    domains: '/staff/domains',
    domainDetail: (id: string | number) => `/staff/domains/${id}`,
    tickets: '/staff/support',
    ticketDetail: (id: string | number) => `/staff/support/${id}`,
  },
  admin: {
    dashboard: '/admin/dashboard',
    users: '/admin/users',
    userDetail: (id: string | number) => `/admin/users/${id}`,
    projects: '/admin/projects',
    projectDetail: (id: string | number) => `/admin/projects/${id}`,
    quotes: '/admin/quotes',
    quoteDetail: (id: string | number) => `/admin/quotes/${id}`,
    invoices: '/admin/invoices',
    invoiceDetail: (id: string | number) => `/admin/invoices/${id}`,
    settings: '/admin/settings',
    hostingPlans: '/admin/hosting/plans',
    hostingAccounts: '/admin/hosting/accounts',
    hostingAccountDetail: (id: string | number) => `/admin/hosting/accounts/${id}`,
    domains: '/admin/domains',
    domainDetail: (id: string | number) => `/admin/domains/${id}`,
    tickets: '/admin/support',
    ticketDetail: (id: string | number) => `/admin/support/${id}`,
    teamMembers: '/admin/team-members',
    services: '/admin/services',
    serviceDetail: (id: string | number) => `/admin/services/${id}`,
  },
  /**
   * The TEAM_MEMBER area. Nothing else lives under /team: a collaborator only
   * ever sees their assigned projects, so there is no quotes/invoices/clients
   * route here to guard.
   */
  team: {
    dashboard: '/team/dashboard',
    projects: '/team/projects',
    projectDetail: (id: string | number) => `/team/projects/${id}`,
  },
} as const

/** Where each role lands after login/register — the one place this mapping is defined. */
export const roleHomePath: Record<Role, string> = {
  ADMIN: paths.admin.dashboard,
  STAFF: paths.staff.overview,
  CLIENT: paths.client.dashboard,
  TEAM_MEMBER: paths.team.dashboard,
}

/**
 * Whether `pathname` falls under the section of the app `role` is allowed into.
 * Mirrors the RoleProtectedRoute wrapping in App.tsx (each of /client, /staff,
 * /admin is gated to exactly one role) — used to validate a post-login redirect
 * target before honoring it, so a saved "from" location never sends a user
 * somewhere their role can't actually go.
 */
export function isPathAllowedForRole(pathname: string, role: Role): boolean {
  switch (role) {
    case 'ADMIN':
      return pathname.startsWith('/admin')
    case 'STAFF':
      return pathname.startsWith('/staff')
    case 'CLIENT':
      return pathname.startsWith('/client')
    case 'TEAM_MEMBER':
      return pathname.startsWith('/team')
    default:
      return false
  }
}
