import { Route, Routes } from 'react-router-dom'
import { LayoutDashboard, FolderKanban, MessageSquare, Users } from 'lucide-react'
import { PublicLayout } from '@/components/layout/PublicLayout'
import { AuthLayout } from '@/components/layout/AuthLayout'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { AdminLayout } from '@/components/layout/AdminLayout'
import { ProtectedRoute } from '@/routes/ProtectedRoute'
import { RoleProtectedRoute } from '@/routes/RoleProtectedRoute'
import { paths } from '@/routes/paths'

import { Home } from '@/pages/public/Home'
import { Services } from '@/pages/public/Services'
import { ServiceDetail } from '@/pages/public/ServiceDetail'
import { RequestQuote } from '@/pages/public/RequestQuote'
import { Login } from '@/pages/auth/Login'
import { Register } from '@/pages/auth/Register'
import { ClientDashboard } from '@/pages/client/Dashboard'
import { ClientProjects } from '@/pages/client/Projects'
import { ClientProjectDetail } from '@/pages/client/ProjectDetail'
import { StaffOverview } from '@/pages/staff/Overview'
import { StaffProjects } from '@/pages/staff/Projects'
import { StaffProjectDetail } from '@/pages/staff/ProjectDetail'
import { StaffQuotes } from '@/pages/staff/Quotes'
import { StaffQuoteDetail } from '@/pages/staff/QuoteDetail'
import { AdminDashboard } from '@/pages/admin/Dashboard'
import { AdminUsers } from '@/pages/admin/Users'
import { AdminUserDetail } from '@/pages/admin/UserDetail'
import { AdminProjects } from '@/pages/admin/Projects'
import { AdminProjectDetail } from '@/pages/admin/ProjectDetail'
import { AdminQuotes } from '@/pages/admin/Quotes'
import { AdminQuoteDetail } from '@/pages/admin/QuoteDetail'
import { NotFound } from '@/pages/NotFound'

const clientNavItems = [
  { label: 'Dashboard', to: paths.client.dashboard, icon: LayoutDashboard },
  { label: 'My Projects', to: paths.client.projects, icon: FolderKanban },
]

const staffNavItems = [
  { label: 'Overview', to: paths.staff.overview, icon: LayoutDashboard, end: true },
  { label: 'Projects', to: paths.staff.projects, icon: FolderKanban },
  { label: 'Quote Requests', to: paths.staff.quotes, icon: MessageSquare },
]

const adminNavItems = [
  { label: 'Dashboard', to: paths.admin.dashboard, icon: LayoutDashboard },
  { label: 'Users', to: paths.admin.users, icon: Users },
  { label: 'Projects', to: paths.admin.projects, icon: FolderKanban },
  { label: 'Quote Requests', to: paths.admin.quotes, icon: MessageSquare },
]

function App() {
  return (
    <Routes>
      {/* Public marketing site */}
      <Route element={<PublicLayout />}>
        <Route path={paths.home} element={<Home />} />
        <Route path={paths.services} element={<Services />} />
        <Route path="/services/:serviceId" element={<ServiceDetail />} />
        <Route path={paths.requestQuote} element={<RequestQuote />} />
      </Route>

      {/* Auth */}
      <Route element={<AuthLayout />}>
        <Route path={paths.login} element={<Login />} />
        <Route path={paths.register} element={<Register />} />
      </Route>

      {/* Authenticated areas — ProtectedRoute checks login, RoleProtectedRoute checks role */}
      <Route element={<ProtectedRoute />}>
        {/* Client area */}
        <Route element={<RoleProtectedRoute allowedRoles={['CLIENT']} />}>
          <Route element={<DashboardLayout roleLabel="Client" navItems={clientNavItems} />}>
            <Route path={paths.client.dashboard} element={<ClientDashboard />} />
            <Route path={paths.client.projects} element={<ClientProjects />} />
            <Route path="/client/projects/:projectId" element={<ClientProjectDetail />} />
          </Route>
        </Route>

        {/* Staff area */}
        <Route element={<RoleProtectedRoute allowedRoles={['STAFF']} />}>
          <Route element={<AdminLayout navItems={staffNavItems} />}>
            <Route path={paths.staff.overview} element={<StaffOverview />} />
            <Route path={paths.staff.projects} element={<StaffProjects />} />
            <Route path="/staff/projects/:projectId" element={<StaffProjectDetail />} />
            <Route path={paths.staff.quotes} element={<StaffQuotes />} />
            <Route path="/staff/quotes/:quoteId" element={<StaffQuoteDetail />} />
          </Route>
        </Route>

        {/* Admin area */}
        <Route element={<RoleProtectedRoute allowedRoles={['ADMIN']} />}>
          <Route element={<AdminLayout navItems={adminNavItems} />}>
            <Route path={paths.admin.dashboard} element={<AdminDashboard />} />
            <Route path={paths.admin.users} element={<AdminUsers />} />
            <Route path="/admin/users/:userId" element={<AdminUserDetail />} />
            <Route path={paths.admin.projects} element={<AdminProjects />} />
            <Route path="/admin/projects/:projectId" element={<AdminProjectDetail />} />
            <Route path={paths.admin.quotes} element={<AdminQuotes />} />
            <Route path="/admin/quotes/:quoteId" element={<AdminQuoteDetail />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
