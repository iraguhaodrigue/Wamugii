import type { components } from '@/types/api'

type Role = components['schemas']['Role']

export const paths = {
  home: '/',
  services: '/services',
  serviceDetail: (id: string | number) => `/services/${id}`,
  requestQuote: '/request-quote',
  login: '/login',
  register: '/register',
  client: {
    dashboard: '/client/dashboard',
    projects: '/client/projects',
    projectDetail: (id: string | number) => `/client/projects/${id}`,
    invoices: '/client/invoices',
    invoiceDetail: (id: string | number) => `/client/invoices/${id}`,
  },
  staff: {
    overview: '/staff',
    projects: '/staff/projects',
    projectDetail: (id: string | number) => `/staff/projects/${id}`,
    quotes: '/staff/quotes',
    quoteDetail: (id: string | number) => `/staff/quotes/${id}`,
    invoices: '/staff/invoices',
    invoiceDetail: (id: string | number) => `/staff/invoices/${id}`,
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
  },
} as const

/** Where each role lands after login/register — the one place this mapping is defined. */
export const roleHomePath: Record<Role, string> = {
  ADMIN: paths.admin.dashboard,
  STAFF: paths.staff.overview,
  CLIENT: paths.client.dashboard,
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
    default:
      return false
  }
}
