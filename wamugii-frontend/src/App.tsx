import { Route, Routes } from 'react-router-dom'
import { PublicLayout } from '@/components/layout/PublicLayout'
import { AuthLayout } from '@/components/layout/AuthLayout'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
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
import { StaffQuotes } from '@/pages/staff/Quotes'
import { AdminDashboard } from '@/pages/admin/Dashboard'
import { AdminUsers } from '@/pages/admin/Users'
import { AdminProjects } from '@/pages/admin/Projects'
import { AdminQuotes } from '@/pages/admin/Quotes'
import { NotFound } from '@/pages/NotFound'

const clientNavItems = [
  { label: 'Dashboard', to: paths.client.dashboard },
  { label: 'My Projects', to: paths.client.projects },
]

const staffNavItems = [
  { label: 'Overview', to: paths.staff.overview },
  { label: 'Projects', to: paths.staff.projects },
  { label: 'Quote Requests', to: paths.staff.quotes },
]

const adminNavItems = [
  { label: 'Dashboard', to: paths.admin.dashboard },
  { label: 'Users', to: paths.admin.users },
  { label: 'Projects', to: paths.admin.projects },
  { label: 'Quote Requests', to: paths.admin.quotes },
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

      {/* Client area */}
      <Route element={<DashboardLayout roleLabel="Client" navItems={clientNavItems} />}>
        <Route path={paths.client.dashboard} element={<ClientDashboard />} />
        <Route path={paths.client.projects} element={<ClientProjects />} />
        <Route path="/client/projects/:projectId" element={<ClientProjectDetail />} />
      </Route>

      {/* Staff area */}
      <Route element={<DashboardLayout roleLabel="Staff" navItems={staffNavItems} />}>
        <Route path={paths.staff.overview} element={<StaffOverview />} />
        <Route path={paths.staff.projects} element={<StaffProjects />} />
        <Route path={paths.staff.quotes} element={<StaffQuotes />} />
      </Route>

      {/* Admin area */}
      <Route element={<DashboardLayout roleLabel="Admin" navItems={adminNavItems} />}>
        <Route path={paths.admin.dashboard} element={<AdminDashboard />} />
        <Route path={paths.admin.users} element={<AdminUsers />} />
        <Route path={paths.admin.projects} element={<AdminProjects />} />
        <Route path={paths.admin.quotes} element={<AdminQuotes />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
