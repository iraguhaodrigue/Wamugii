import { Suspense } from 'react'
import { Route, Routes } from 'react-router-dom'
import {
  FolderKanban,
  LayoutDashboard,
  LifeBuoy,
  MessageSquare,
  Boxes,
  UserCheck,
  GraduationCap,
  Receipt,
  Globe,
  Server,
  Settings,
  Users,
} from 'lucide-react'
import { PublicLayout } from '@/components/layout/PublicLayout'
import { ProtectedRoute } from '@/routes/ProtectedRoute'
import { RoleProtectedRoute } from '@/routes/RoleProtectedRoute'
import { paths } from '@/routes/paths'
import { PageLoader } from '@/components/common/PageLoader'
import { lazyNamed } from '@/lib/lazyPage'

// Every page except the home page is loaded only when someone opens it, so a
// visitor's first download is small and the home page appears much sooner.
const AuthLayout = lazyNamed(() => import('@/components/layout/AuthLayout'), 'AuthLayout')
const DashboardLayout = lazyNamed(() => import('@/components/layout/DashboardLayout'), 'DashboardLayout')
const AdminLayout = lazyNamed(() => import('@/components/layout/AdminLayout'), 'AdminLayout')
const Services = lazyNamed(() => import('@/pages/public/Services'), 'Services')
const ServiceDetail = lazyNamed(() => import('@/pages/public/ServiceDetail'), 'ServiceDetail')
const RequestQuote = lazyNamed(() => import('@/pages/public/RequestQuote'), 'RequestQuote')
const Hosting = lazyNamed(() => import('@/pages/public/Hosting'), 'Hosting')
const Courses = lazyNamed(() => import('@/pages/public/Courses'), 'Courses')
const CourseDetail = lazyNamed(() => import('@/pages/public/CourseDetail'), 'CourseDetail')
const Login = lazyNamed(() => import('@/pages/auth/Login'), 'Login')
const Register = lazyNamed(() => import('@/pages/auth/Register'), 'Register')
const ForgotPassword = lazyNamed(() => import('@/pages/auth/ForgotPassword'), 'ForgotPassword')
const ResetPassword = lazyNamed(() => import('@/pages/auth/ResetPassword'), 'ResetPassword')
const JoinTeam = lazyNamed(() => import('@/pages/auth/JoinTeam'), 'JoinTeam')
const PendingApproval = lazyNamed(() => import('@/pages/auth/PendingApproval'), 'PendingApproval')
const ClientDashboard = lazyNamed(() => import('@/pages/client/Dashboard'), 'ClientDashboard')
const ClientProjects = lazyNamed(() => import('@/pages/client/Projects'), 'ClientProjects')
const ClientProjectDetail = lazyNamed(() => import('@/pages/client/ProjectDetail'), 'ClientProjectDetail')
const ClientInvoices = lazyNamed(() => import('@/pages/client/Invoices'), 'ClientInvoices')
const ClientInvoiceDetail = lazyNamed(() => import('@/pages/client/InvoiceDetail'), 'ClientInvoiceDetail')
const ClientHosting = lazyNamed(() => import('@/pages/client/Hosting'), 'ClientHosting')
const ClientHostingDetail = lazyNamed(() => import('@/pages/client/HostingDetail'), 'ClientHostingDetail')
const ClientDomains = lazyNamed(() => import('@/pages/client/Domains'), 'ClientDomains')
const ClientLearning = lazyNamed(() => import('@/pages/client/Learning'), 'ClientLearning')
const ClientCoursePlayer = lazyNamed(() => import('@/pages/client/CoursePlayer'), 'ClientCoursePlayer')
const ClientCourseExam = lazyNamed(() => import('@/pages/client/CourseExam'), 'ClientCourseExam')
const InstructorDashboard = lazyNamed(() => import('@/pages/instructor/InstructorDashboard'), 'InstructorDashboard')
const InstructorQuestions = lazyNamed(() => import('@/pages/instructor/InstructorQuestions'), 'InstructorQuestions')
const ClientDomainDetail = lazyNamed(() => import('@/pages/client/DomainDetail'), 'ClientDomainDetail')
const ClientQuoteDetail = lazyNamed(() => import('@/pages/client/QuoteDetail'), 'ClientQuoteDetail')
const ClientTickets = lazyNamed(() => import('@/pages/client/Tickets'), 'ClientTickets')
const ClientTicketDetail = lazyNamed(() => import('@/pages/client/TicketDetail'), 'ClientTicketDetail')
const StaffOverview = lazyNamed(() => import('@/pages/staff/Overview'), 'StaffOverview')
const StaffProjects = lazyNamed(() => import('@/pages/staff/Projects'), 'StaffProjects')
const StaffProjectDetail = lazyNamed(() => import('@/pages/staff/ProjectDetail'), 'StaffProjectDetail')
const StaffQuotes = lazyNamed(() => import('@/pages/staff/Quotes'), 'StaffQuotes')
const StaffQuoteDetail = lazyNamed(() => import('@/pages/staff/QuoteDetail'), 'StaffQuoteDetail')
const StaffInvoices = lazyNamed(() => import('@/pages/staff/Invoices'), 'StaffInvoices')
const StaffInvoiceDetail = lazyNamed(() => import('@/pages/staff/InvoiceDetail'), 'StaffInvoiceDetail')
const StaffHostingAccounts = lazyNamed(() => import('@/pages/staff/HostingAccounts'), 'StaffHostingAccounts')
const StaffHostingAccountDetail = lazyNamed(() => import('@/pages/staff/HostingAccountDetail'), 'StaffHostingAccountDetail')
const StaffDomains = lazyNamed(() => import('@/pages/staff/Domains'), 'StaffDomains')
const StaffDomainDetail = lazyNamed(() => import('@/pages/staff/DomainDetail'), 'StaffDomainDetail')
const StaffTickets = lazyNamed(() => import('@/pages/staff/Tickets'), 'StaffTickets')
const StaffTicketDetail = lazyNamed(() => import('@/pages/staff/TicketDetail'), 'StaffTicketDetail')
const AdminDashboard = lazyNamed(() => import('@/pages/admin/Dashboard'), 'AdminDashboard')
const AdminUsers = lazyNamed(() => import('@/pages/admin/Users'), 'AdminUsers')
const AdminUserDetail = lazyNamed(() => import('@/pages/admin/UserDetail'), 'AdminUserDetail')
const AdminProjects = lazyNamed(() => import('@/pages/admin/Projects'), 'AdminProjects')
const AdminProjectDetail = lazyNamed(() => import('@/pages/admin/ProjectDetail'), 'AdminProjectDetail')
const AdminQuotes = lazyNamed(() => import('@/pages/admin/Quotes'), 'AdminQuotes')
const AdminQuoteDetail = lazyNamed(() => import('@/pages/admin/QuoteDetail'), 'AdminQuoteDetail')
const AdminInvoices = lazyNamed(() => import('@/pages/admin/Invoices'), 'AdminInvoices')
const AdminSettings = lazyNamed(() => import('@/pages/admin/Settings'), 'AdminSettings')
const AdminHostingPlans = lazyNamed(() => import('@/pages/admin/HostingPlans'), 'AdminHostingPlans')
const AdminHostingAccounts = lazyNamed(() => import('@/pages/admin/HostingAccounts'), 'AdminHostingAccounts')
const AdminHostingAccountDetail = lazyNamed(() => import('@/pages/admin/HostingAccountDetail'), 'AdminHostingAccountDetail')
const AdminDomains = lazyNamed(() => import('@/pages/admin/Domains'), 'AdminDomains')
const AdminDomainDetail = lazyNamed(() => import('@/pages/admin/DomainDetail'), 'AdminDomainDetail')
const AdminTickets = lazyNamed(() => import('@/pages/admin/Tickets'), 'AdminTickets')
const AdminTicketDetail = lazyNamed(() => import('@/pages/admin/TicketDetail'), 'AdminTicketDetail')
const AdminTeamMembers = lazyNamed(() => import('@/pages/admin/TeamMembers'), 'AdminTeamMembers')
const AdminCourses = lazyNamed(() => import('@/pages/admin/Courses'), 'AdminCourses')
const AdminCourseDetail = lazyNamed(() => import('@/pages/admin/CourseDetail'), 'AdminCourseDetail')
const AdminServices = lazyNamed(() => import('@/pages/admin/Services'), 'AdminServices')
const AdminServiceDetail = lazyNamed(() => import('@/pages/admin/ServiceDetail'), 'AdminServiceDetail')
const TeamDashboard = lazyNamed(() => import('@/pages/team/Dashboard'), 'TeamDashboard')
const TeamProjects = lazyNamed(() => import('@/pages/team/Projects'), 'TeamProjects')
const TeamProjectDetail = lazyNamed(() => import('@/pages/team/ProjectDetail'), 'TeamProjectDetail')
const AdminInvoiceDetail = lazyNamed(() => import('@/pages/admin/InvoiceDetail'), 'AdminInvoiceDetail')
const NotFound = lazyNamed(() => import('@/pages/NotFound'), 'NotFound')

import { Home } from '@/pages/public/Home'

const clientNavItems = [
  { label: 'Dashboard', to: paths.client.dashboard, icon: LayoutDashboard },
  { label: 'My Projects', to: paths.client.projects, icon: FolderKanban },
  { label: 'My Invoices', to: paths.client.invoices, icon: Receipt },
  { label: 'My Hosting', to: paths.client.hosting, icon: Server },
  { label: 'My Domains', to: paths.client.domains, icon: Globe },
  { label: 'My Learning', to: paths.client.learning, icon: GraduationCap },
  { label: 'Support', to: paths.client.tickets, icon: LifeBuoy },
]

const teamNavItems = [
  { label: 'Dashboard', to: paths.team.dashboard, icon: LayoutDashboard },
  { label: 'My Projects', to: paths.team.projects, icon: FolderKanban },
]

const instructorNavItems = [
  { label: 'My Courses', to: paths.instructor.dashboard, icon: GraduationCap, end: true },
  { label: 'Student Questions', to: paths.instructor.questions, icon: MessageSquare },
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
  { label: 'Services', to: paths.admin.services, icon: Boxes },
  { label: 'Courses', to: paths.admin.courses, icon: GraduationCap },
  { label: 'Projects', to: paths.admin.projects, icon: FolderKanban },
  { label: 'Quote Requests', to: paths.admin.quotes, icon: MessageSquare },
  { label: 'Invoices', to: paths.admin.invoices, icon: Receipt },
  { label: 'Hosting', to: paths.admin.hostingAccounts, icon: Server },
  { label: 'Hosting Plans', to: paths.admin.hostingPlans, icon: Server },
  { label: 'Domains', to: paths.admin.domains, icon: Globe },
  { label: 'Support Tickets', to: paths.admin.tickets, icon: LifeBuoy },
  { label: 'Team Members', to: paths.admin.teamMembers, icon: UserCheck },
  { label: 'Settings', to: paths.admin.settings, icon: Settings },
]

function App() {
  return (
    <Suspense fallback={<PageLoader fullScreen />}>
    <Routes>
      {/* Public marketing site */}
      <Route element={<PublicLayout />}>
        <Route path={paths.home} element={<Home />} />
        <Route path={paths.services} element={<Services />} />
        <Route path="/services/:serviceId" element={<ServiceDetail />} />
        <Route path={paths.requestQuote} element={<RequestQuote />} />
        <Route path={paths.hosting} element={<Hosting />} />
        <Route path={paths.courses} element={<Courses />} />
        <Route path="/courses/:slug" element={<CourseDetail />} />
      </Route>

      {/* Auth */}
      <Route element={<AuthLayout />}>
        <Route path={paths.login} element={<Login />} />
        <Route path={paths.register} element={<Register />} />
        {/* Public: the user is locked out, so no auth guard. */}
        <Route path={paths.forgotPassword} element={<ForgotPassword />} />
        <Route path={paths.resetPassword} element={<ResetPassword />} />
        {/* Public: collaborators self-register here and wait for approval. */}
        <Route path={paths.joinTeam} element={<JoinTeam />} />
      </Route>

      {/* The awaiting-approval screen: authenticated but deliberately outside
          ProtectedRoute, which is what redirects an unapproved account here. */}
      <Route element={<AuthLayout />}>
        <Route path={paths.pendingApproval} element={<PendingApproval />} />
      </Route>

      {/* Authenticated areas — ProtectedRoute checks login and approval,
          RoleProtectedRoute checks role */}
      <Route element={<ProtectedRoute />}>
        {/* Client area */}
        <Route element={<RoleProtectedRoute allowedRoles={['CLIENT']} />}>
          {/* The final exam runs full screen, without the dashboard around it. */}
          <Route path="/client/learning/:slug/exam" element={<ClientCourseExam />} />
          <Route element={<DashboardLayout roleLabel="Client" navItems={clientNavItems} />}>
            <Route path={paths.client.dashboard} element={<ClientDashboard />} />
            <Route path={paths.client.projects} element={<ClientProjects />} />
            <Route path="/client/projects/:projectId" element={<ClientProjectDetail />} />
            <Route path={paths.client.invoices} element={<ClientInvoices />} />
            <Route path="/client/invoices/:invoiceId" element={<ClientInvoiceDetail />} />
            <Route path={paths.client.hosting} element={<ClientHosting />} />
            <Route path="/client/hosting/:accountId" element={<ClientHostingDetail />} />
            <Route path={paths.client.domains} element={<ClientDomains />} />
            <Route path={paths.client.learning} element={<ClientLearning />} />
            <Route path="/client/learning/:slug" element={<ClientCoursePlayer />} />
            <Route path="/client/domains/:domainId" element={<ClientDomainDetail />} />
            {/* Detail only: the dashboard lists their recent quotes. */}
            <Route path="/client/quotes/:quoteId" element={<ClientQuoteDetail />} />
            <Route path={paths.client.tickets} element={<ClientTickets />} />
            <Route path="/client/support/:ticketId" element={<ClientTicketDetail />} />
          </Route>
        </Route>

        {/* Team member area — assigned projects only, no client data anywhere */}
        <Route element={<RoleProtectedRoute allowedRoles={['TEAM_MEMBER']} />}>
          <Route element={<DashboardLayout roleLabel="Team Member" navItems={teamNavItems} />}>
            <Route path={paths.team.dashboard} element={<TeamDashboard />} />
            <Route path={paths.team.projects} element={<TeamProjects />} />
            <Route path="/team/projects/:projectId" element={<TeamProjectDetail />} />
          </Route>
        </Route>

        {/* Instructor area — only the courses an admin assigned to them */}
        <Route element={<RoleProtectedRoute allowedRoles={['INSTRUCTOR']} />}>
          <Route element={<AdminLayout navItems={instructorNavItems} />}>
            <Route path={paths.instructor.dashboard} element={<InstructorDashboard />} />
            <Route path={paths.instructor.questions} element={<InstructorQuestions />} />
            <Route path="/instructor/courses/:courseId" element={<AdminCourseDetail />} />
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
            <Route path={paths.admin.services} element={<AdminServices />} />
            <Route path="/admin/services/:serviceId" element={<AdminServiceDetail />} />
            <Route path={paths.admin.teamMembers} element={<AdminTeamMembers />} />
            <Route path={paths.admin.courses} element={<AdminCourses />} />
            <Route path="/admin/courses/:courseId" element={<AdminCourseDetail />} />
            <Route path={paths.admin.settings} element={<AdminSettings />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
    </Suspense>
  )
}

export default App
