import { Route, Routes } from 'react-router-dom'
import {
  FolderKanban,
  LayoutDashboard,
  LifeBuoy,
  MessageSquare,
  Receipt,
  Globe,
  Server,
  Settings,
  Users,
} from 'lucide-react'
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
import { Hosting } from '@/pages/public/Hosting'
import { Login } from '@/pages/auth/Login'
import { Register } from '@/pages/auth/Register'
import { ForgotPassword } from '@/pages/auth/ForgotPassword'
import { ResetPassword } from '@/pages/auth/ResetPassword'
import { ClientDashboard } from '@/pages/client/Dashboard'
import { ClientProjects } from '@/pages/client/Projects'
import { ClientProjectDetail } from '@/pages/client/ProjectDetail'
import { ClientInvoices } from '@/pages/client/Invoices'
import { ClientInvoiceDetail } from '@/pages/client/InvoiceDetail'
import { ClientHosting } from '@/pages/client/Hosting'
import { ClientHostingDetail } from '@/pages/client/HostingDetail'
import { ClientDomains } from '@/pages/client/Domains'
import { ClientDomainDetail } from '@/pages/client/DomainDetail'
import { ClientQuoteDetail } from '@/pages/client/QuoteDetail'
import { ClientTickets } from '@/pages/client/Tickets'
import { ClientTicketDetail } from '@/pages/client/TicketDetail'
import { StaffOverview } from '@/pages/staff/Overview'
import { StaffProjects } from '@/pages/staff/Projects'
import { StaffProjectDetail } from '@/pages/staff/ProjectDetail'
import { StaffQuotes } from '@/pages/staff/Quotes'
import { StaffQuoteDetail } from '@/pages/staff/QuoteDetail'
import { StaffInvoices } from '@/pages/staff/Invoices'
import { StaffInvoiceDetail } from '@/pages/staff/InvoiceDetail'
import { StaffHostingAccounts } from '@/pages/staff/HostingAccounts'
import { StaffHostingAccountDetail } from '@/pages/staff/HostingAccountDetail'
import { StaffDomains } from '@/pages/staff/Domains'
import { StaffDomainDetail } from '@/pages/staff/DomainDetail'
import { StaffTickets } from '@/pages/staff/Tickets'
import { StaffTicketDetail } from '@/pages/staff/TicketDetail'
import { AdminDashboard } from '@/pages/admin/Dashboard'
import { AdminUsers } from '@/pages/admin/Users'
import { AdminUserDetail } from '@/pages/admin/UserDetail'
import { AdminProjects } from '@/pages/admin/Projects'
import { AdminProjectDetail } from '@/pages/admin/ProjectDetail'
import { AdminQuotes } from '@/pages/admin/Quotes'
import { AdminQuoteDetail } from '@/pages/admin/QuoteDetail'
import { AdminInvoices } from '@/pages/admin/Invoices'
import { AdminSettings } from '@/pages/admin/Settings'
import { AdminHostingPlans } from '@/pages/admin/HostingPlans'
import { AdminHostingAccounts } from '@/pages/admin/HostingAccounts'
import { AdminHostingAccountDetail } from '@/pages/admin/HostingAccountDetail'
import { AdminDomains } from '@/pages/admin/Domains'
import { AdminDomainDetail } from '@/pages/admin/DomainDetail'
import { AdminTickets } from '@/pages/admin/Tickets'
import { AdminTicketDetail } from '@/pages/admin/TicketDetail'
import { AdminInvoiceDetail } from '@/pages/admin/InvoiceDetail'
import { NotFound } from '@/pages/NotFound'

const clientNavItems = [
  { label: 'Dashboard', to: paths.client.dashboard, icon: LayoutDashboard },
  { label: 'My Projects', to: paths.client.projects, icon: FolderKanban },
  { label: 'My Invoices', to: paths.client.invoices, icon: Receipt },
  { label: 'My Hosting', to: paths.client.hosting, icon: Server },
  { label: 'My Domains', to: paths.client.domains, icon: Globe },
  { label: 'Support', to: paths.client.tickets, icon: LifeBuoy },
]

const staffNavItems = [
  { label: 'Overview', to: paths.staff.overview, icon: LayoutDashboard, end: true },
  { label: 'Projects', to: paths.staff.projects, icon: FolderKanban },
  { label: 'Quote Requests', to: paths.staff.quotes, icon: MessageSquare },
  { label: 'Invoices', to: paths.staff.invoices, icon: Receipt },
  { label: 'Hosting', to: paths.staff.hostingAccounts, icon: Server },
  { label: 'Domains', to: paths.staff.domains, icon: Globe },
  { label: 'Support Tickets', to: paths.staff.tickets, icon: LifeBuoy },
]

const adminNavItems = [
  { label: 'Dashboard', to: paths.admin.dashboard, icon: LayoutDashboard },
  { label: 'Users', to: paths.admin.users, icon: Users },
  { label: 'Projects', to: paths.admin.projects, icon: FolderKanban },
  { label: 'Quote Requests', to: paths.admin.quotes, icon: MessageSquare },
  { label: 'Invoices', to: paths.admin.invoices, icon: Receipt },
  { label: 'Hosting', to: paths.admin.hostingAccounts, icon: Server },
  { label: 'Hosting Plans', to: paths.admin.hostingPlans, icon: Server },
  { label: 'Domains', to: paths.admin.domains, icon: Globe },
  { label: 'Support Tickets', to: paths.admin.tickets, icon: LifeBuoy },
  { label: 'Settings', to: paths.admin.settings, icon: Settings },
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
        <Route path={paths.hosting} element={<Hosting />} />
      </Route>

      {/* Auth */}
      <Route element={<AuthLayout />}>
        <Route path={paths.login} element={<Login />} />
        <Route path={paths.register} element={<Register />} />
        {/* Public: the user is locked out, so no auth guard. */}
        <Route path={paths.forgotPassword} element={<ForgotPassword />} />
        <Route path={paths.resetPassword} element={<ResetPassword />} />
      </Route>

      {/* Authenticated areas — ProtectedRoute checks login, RoleProtectedRoute checks role */}
      <Route element={<ProtectedRoute />}>
        {/* Client area */}
        <Route element={<RoleProtectedRoute allowedRoles={['CLIENT']} />}>
          <Route element={<DashboardLayout roleLabel="Client" navItems={clientNavItems} />}>
            <Route path={paths.client.dashboard} element={<ClientDashboard />} />
            <Route path={paths.client.projects} element={<ClientProjects />} />
            <Route path="/client/projects/:projectId" element={<ClientProjectDetail />} />
            <Route path={paths.client.invoices} element={<ClientInvoices />} />
            <Route path="/client/invoices/:invoiceId" element={<ClientInvoiceDetail />} />
            <Route path={paths.client.hosting} element={<ClientHosting />} />
            <Route path="/client/hosting/:accountId" element={<ClientHostingDetail />} />
            <Route path={paths.client.domains} element={<ClientDomains />} />
            <Route path="/client/domains/:domainId" element={<ClientDomainDetail />} />
            {/* Detail only: the dashboard lists their recent quotes. */}
            <Route path="/client/quotes/:quoteId" element={<ClientQuoteDetail />} />
            <Route path={paths.client.tickets} element={<ClientTickets />} />
            <Route path="/client/support/:ticketId" element={<ClientTicketDetail />} />
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
            <Route path={paths.staff.invoices} element={<StaffInvoices />} />
            <Route path="/staff/invoices/:invoiceId" element={<StaffInvoiceDetail />} />
            <Route path={paths.staff.hostingAccounts} element={<StaffHostingAccounts />} />
            <Route path="/staff/hosting/accounts/:accountId" element={<StaffHostingAccountDetail />} />
            <Route path={paths.staff.domains} element={<StaffDomains />} />
            <Route path="/staff/domains/:domainId" element={<StaffDomainDetail />} />
            <Route path={paths.staff.tickets} element={<StaffTickets />} />
            <Route path="/staff/support/:ticketId" element={<StaffTicketDetail />} />
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
            <Route path={paths.admin.invoices} element={<AdminInvoices />} />
            <Route path="/admin/invoices/:invoiceId" element={<AdminInvoiceDetail />} />
            <Route path={paths.admin.hostingPlans} element={<AdminHostingPlans />} />
            <Route path={paths.admin.hostingAccounts} element={<AdminHostingAccounts />} />
            <Route path="/admin/hosting/accounts/:accountId" element={<AdminHostingAccountDetail />} />
            <Route path={paths.admin.domains} element={<AdminDomains />} />
            <Route path="/admin/domains/:domainId" element={<AdminDomainDetail />} />
            <Route path={paths.admin.tickets} element={<AdminTickets />} />
            <Route path="/admin/support/:ticketId" element={<AdminTicketDetail />} />
            <Route path={paths.admin.settings} element={<AdminSettings />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
