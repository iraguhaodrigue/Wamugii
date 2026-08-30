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
  },
  staff: {
    overview: '/staff',
    projects: '/staff/projects',
    quotes: '/staff/quotes',
  },
  admin: {
    dashboard: '/admin/dashboard',
    users: '/admin/users',
    projects: '/admin/projects',
    quotes: '/admin/quotes',
  },
} as const
