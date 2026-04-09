import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// ── Lazy-loaded views ─────────────────────────────────────────────────────────
const LoginView         = () => import('@/views/auth/LoginView.vue')
const DashboardView     = () => import('@/views/dashboard/DashboardView.vue')
const MembersListView   = () => import('@/views/members/MembersListView.vue')
const MemberDetailView  = () => import('@/views/members/MemberDetailView.vue')
const MemberFormView    = () => import('@/views/members/MemberFormView.vue')
const FinanceView       = () => import('@/views/finance/FinanceView.vue')
const TransactionForm   = () => import('@/views/finance/TransactionFormView.vue')
const CausesView        = () => import('@/views/finance/CausesView.vue')
const PledgesView       = () => import('@/views/finance/PledgesView.vue')
const EventsView        = () => import('@/views/events/EventsView.vue')
const EventDetailView   = () => import('@/views/events/EventDetailView.vue')
const WorkersView       = () => import('@/views/workers/WorkersView.vue')
const PayrollView       = () => import('@/views/workers/PayrollView.vue')
const LeaveView         = () => import('@/views/workers/LeaveView.vue')
const SermonsView       = () => import('@/views/sermons/SermonsView.vue')
const SermonDetailView  = () => import('@/views/sermons/SermonDetailView.vue')
const BudgetView        = () => import('@/views/budget/BudgetView.vue')
const InventoryView     = () => import('@/views/inventory/InventoryView.vue')
const ProcurementView   = () => import('@/views/procurement/ProcurementView.vue')
const CommunicationView = () => import('@/views/communication/CommunicationView.vue')
const FollowUpView      = () => import('@/views/followup/FollowUpView.vue')
const PrayerView        = () => import('@/views/prayer/PrayerView.vue')
const DiscipleshipView  = () => import('@/views/discipleship/DiscipleshipView.vue')
const AuditView         = () => import('@/views/audit/AuditView.vue')
const FacilityView      = () => import('@/views/facility/FacilityView.vue')
const ReportsView       = () => import('@/views/reports/ReportsView.vue')
const AIAssistantView   = () => import('@/views/ai/AIAssistantView.vue')
const SettingsView      = () => import('@/views/settings/SettingsView.vue')
const UsersView         = () => import('@/views/settings/UsersView.vue')
const ProfileView       = () => import('@/views/auth/ProfileView.vue')
const NotFoundView      = () => import('@/views/NotFoundView.vue')

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '',           redirect: '/dashboard' },
      { path: 'dashboard',  name: 'dashboard',     component: DashboardView },
      // Members
      { path: 'members',          name: 'members',       component: MembersListView },
      { path: 'members/new',      name: 'member-new',    component: MemberFormView },
      { path: 'members/:id',      name: 'member-detail', component: MemberDetailView },
      { path: 'members/:id/edit', name: 'member-edit',   component: MemberFormView },
      // Finance
      { path: 'finance',          name: 'finance',        component: FinanceView },
      { path: 'finance/new',      name: 'transaction-new', component: TransactionForm },
      { path: 'finance/causes',   name: 'causes',          component: CausesView },
      { path: 'finance/pledges',  name: 'pledges',         component: PledgesView },
      // Events
      { path: 'events',       name: 'events',       component: EventsView },
      { path: 'events/:id',   name: 'event-detail', component: EventDetailView },
      // Workers
      { path: 'workers',        name: 'workers',   component: WorkersView },
      { path: 'workers/payroll', name: 'payroll',  component: PayrollView },
      { path: 'workers/leave',   name: 'leave',    component: LeaveView },
      // Sermons
      { path: 'sermons',      name: 'sermons',       component: SermonsView },
      { path: 'sermons/:id',  name: 'sermon-detail', component: SermonDetailView },
      // Other modules
      { path: 'budget',         name: 'budget',        component: BudgetView },
      { path: 'inventory',      name: 'inventory',     component: InventoryView },
      { path: 'procurement',    name: 'procurement',   component: ProcurementView },
      { path: 'communication',  name: 'communication', component: CommunicationView },
      { path: 'followup',       name: 'followup',      component: FollowUpView },
      { path: 'prayer',         name: 'prayer',        component: PrayerView },
      { path: 'discipleship',   name: 'discipleship',  component: DiscipleshipView },
      { path: 'audit',          name: 'audit',         component: AuditView },
      { path: 'facility',       name: 'facility',      component: FacilityView },
      { path: 'reports',        name: 'reports',       component: ReportsView },
      { path: 'ai',             name: 'ai-assistant',  component: AIAssistantView },
      // Settings
      { path: 'settings',       name: 'settings',      component: SettingsView,
        meta: { roles: ['super_admin', 'administrator'] } },
      { path: 'settings/users', name: 'users',         component: UsersView,
        meta: { roles: ['super_admin', 'administrator'] } },
      { path: 'profile',        name: 'profile',       component: ProfileView },
    ]
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.public) return next()

  if (to.meta.requiresAuth || to.matched.some(r => r.meta.requiresAuth)) {
    if (!auth.isAuthenticated) return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.roles) {
    if (!to.meta.roles.includes(auth.userRole)) return next({ name: 'dashboard' })
  }

  next()
})

export default router
