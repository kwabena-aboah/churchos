<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">{{ greeting }}, {{ auth.user?.first_name }}. Here's your overview.</p>
      </div>
      <div class="d-flex gap-2">
        <select class="form-select form-select-sm" v-model="period" @change="loadData" style="width:130px">
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
          <option value="this_year">This Year</option>
        </select>
        <button class="btn btn-primary btn-sm" @click="loadData">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>
    </div>

    <!-- ── Stat cards ── -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3" v-for="stat in stats" :key="stat.label">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: stat.bg }">
            <i :class="`bi ${stat.icon}`" :style="{ color: stat.color }"></i>
          </div>
          <div>
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'text-success' : 'text-danger'" v-if="stat.trend !== undefined">
              <i :class="`bi bi-arrow-${stat.trend >= 0 ? 'up' : 'down'}`"></i>
              {{ Math.abs(stat.trend) }}% vs last month
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Charts row ── -->
    <div class="row g-3 mb-4">
      <div class="col-lg-8">
        <div class="cos-card">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h6 class="fw-bold mb-0">Monthly Income Trend</h6>
            <span class="badge bg-success-subtle text-success">{{ currentYear }}</span>
          </div>
          <div class="chart-wrapper">
            <Line v-if="incomeChartData" :data="incomeChartData" :options="lineOptions" />
            <div v-else class="cos-spinner"><div class="spinner-border spinner-border-sm"></div></div>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="cos-card">
          <h6 class="fw-bold mb-3">Income Breakdown</h6>
          <div class="chart-wrapper">
            <Doughnut v-if="breakdownData" :data="breakdownData" :options="doughnutOptions" />
            <div v-else class="cos-spinner"><div class="spinner-border spinner-border-sm"></div></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Second charts row ── -->
    <div class="row g-3 mb-4">
      <div class="col-lg-6">
        <div class="cos-card" style="height: 300px;">
          <h6 class="fw-bold mb-3">Membership by Status</h6>
          <Bar v-if="memberChartData" :data="memberChartData" :options="barOptions" />
          <div v-else class="cos-spinner"><div class="spinner-border spinner-border-sm"></div></div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="cos-card" style="height: 300px;">
          <h6 class="fw-bold mb-3">Follow-Up Cases</h6>
          <Doughnut v-if="followupChartData" :data="followupChartData" :options="doughnutOptions" />
          <div v-else class="cos-spinner"><div class="spinner-border spinner-border-sm"></div></div>
        </div>
      </div>
    </div>

    <!-- ── Bottom row ── -->
    <div class="row g-3">
      <!-- Recent transactions -->
      <div class="col-lg-7">
        <div class="cos-card">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h6 class="fw-bold mb-0">Recent Transactions</h6>
            <RouterLink to="/finance" class="btn btn-sm btn-outline-primary">View All</RouterLink>
          </div>
          <div v-if="recentTransactions.length === 0" class="cos-empty">
            <i class="bi bi-receipt"></i><p>No transactions yet</p>
          </div>
          <table class="cos-table" v-else>
            <thead><tr><th>Date</th><th>Member</th><th>Type</th><th>Amount</th></tr></thead>
            <tbody>
              <tr v-for="t in recentTransactions" :key="t.id">
                <td>{{ formatDate(t.transaction_date) }}</td>
                <td>{{ t.member_name }}</td>
                <td><span class="status-badge badge-visitor">{{ t.transaction_type }}</span></td>
                <td class="fw-semibold text-success">{{ fmtCur(t.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Upcoming events + quick actions -->
      <div class="col-lg-5">
        <div class="cos-card mb-3">
          <div class="d-flex align-items-center justify-content-between mb-3">
            <h6 class="fw-bold mb-0">Upcoming Events</h6>
            <RouterLink to="/events" class="btn btn-sm btn-outline-primary">All</RouterLink>
          </div>
          <div v-if="upcomingEvents.length === 0" class="cos-empty">
            <i class="bi bi-calendar-x"></i><p>No upcoming events</p>
          </div>
          <div v-for="ev in upcomingEvents" :key="ev.id" class="event-row">
            <div class="event-date-badge">
              <span class="ev-month">{{ dayjs(ev.start_datetime).format('MMM') }}</span>
              <span class="ev-day">{{ dayjs(ev.start_datetime).format('DD') }}</span>
            </div>
            <div class="flex-grow-1">
              <div class="fw-semibold small">{{ ev.title }}</div>
              <div class="text-muted" style="font-size:11px">{{ dayjs(ev.start_datetime).format('h:mm A') }} · {{ ev.venue_name || 'Church' }}</div>
            </div>
          </div>
        </div>

        <div class="cos-card">
          <h6 class="fw-bold mb-3">Quick Actions</h6>
          <div class="quick-actions">
            <RouterLink to="/members/new" class="qa-btn">
              <i class="bi bi-person-plus"></i><span>Add Member</span>
            </RouterLink>
            <RouterLink to="/finance/new" class="qa-btn">
              <i class="bi bi-plus-circle"></i><span>Record Giving</span>
            </RouterLink>
            <RouterLink to="/followup" class="qa-btn">
              <i class="bi bi-chat-dots"></i><span>Follow-Up</span>
            </RouterLink>
            <RouterLink to="/communication" class="qa-btn">
              <i class="bi bi-megaphone"></i><span>Broadcast</span>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler
} from 'chart.js'
import dayjs from 'dayjs'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { financeApi, membersApi, eventsApi, followupApi } from '@/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend, Filler)

const auth = useAuthStore()
const settingsStore = useSettingsStore()
const period = ref('this_month')
const currentYear = dayjs().year()

const greeting = computed(() => {
  const h = dayjs().hour()
  return h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'
})

const stats = ref([
  { label: 'Active Members', value: '—', icon: 'bi-people-fill', bg: '#e8f5ee', color: '#1a6b3c' },
  { label: 'Total Income', value: '—', icon: 'bi-cash-coin', bg: '#fff3cd', color: '#856404' },
  { label: 'This Month', value: '—', icon: 'bi-calendar-check', bg: '#dbeafe', color: '#1e40af' },
  { label: 'Open Follow-Ups', value: '—', icon: 'bi-chat-heart', bg: '#fce7f3', color: '#9d174d' },
])

const recentTransactions = ref([])
const upcomingEvents = ref([])
const incomeChartData = ref(null)
const breakdownData = ref(null)
const memberChartData = ref(null)
const followupChartData = ref(null)

const fmtCur = (v) => settingsStore.formatCurrency(v)
const formatDate = (d) => dayjs(d).format('DD MMM')

const lineOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, grid: { color: '#f0f0f0' } }, x: { grid: { display: false } } }
}
const barOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true }, x: { grid: { display: false } } }
}
const doughnutOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 16 } } },
  cutout: '65%'
}

async function loadData() {
  try {
    // Summary
    const { data: summary } = await financeApi.summary({ period: period.value })
    stats.value[0].value = summary.active_members || '—'
    stats.value[1].value = fmtCur(summary.total_income || 0)
    stats.value[2].value = fmtCur(summary.this_month || 0)
    stats.value[3].value = summary.open_followups || '—'

    // Monthly chart
    const { data: monthly } = await financeApi.monthlyChart({ year: currentYear })
    if (monthly.labels) {
      incomeChartData.value = {
        labels: monthly.labels,
        datasets: [{
          label: 'Income',
          data: monthly.income,
          borderColor: '#1a6b3c',
          backgroundColor: 'rgba(26,107,60,0.08)',
          fill: true, tension: 0.4, pointRadius: 4,
        }]
      }
      breakdownData.value = {
        labels: ['Tithes', 'Offerings', 'Donations', 'Other'],
        datasets: [{
          data: [monthly.tithes_total, monthly.offerings_total, monthly.donations_total, monthly.other_total],
          backgroundColor: ['#1a6b3c', '#c9a84c', '#2563eb', '#9333ea'],
          borderWidth: 0,
        }]
      }
    }

    // Recent transactions
    const { data: txns } = await financeApi.listTransactions({ page_size: 8, ordering: '-transaction_date' })
    recentTransactions.value = txns.results || txns

    // Upcoming events
    const { data: events } = await eventsApi.upcoming()
    upcomingEvents.value = events.slice(0, 5)

    // Member chart
    memberChartData.value = {
      labels: ['Active', 'Visitor', 'Inactive', 'Transferred'],
      datasets: [{
        data: [summary.active_members || 0, summary.visitors || 0, summary.inactive || 0, summary.transferred || 0],
        backgroundColor: ['#1a6b3c', '#c9a84c', '#6b7280', '#dc2626'],
        borderRadius: 6,
      }]
    }

    // Followup chart
    const { data: fuData } = await followupApi.list({ page_size: 100 })
    const cases = fuData.results || fuData
    const open = cases.filter(c => c.status === 'open').length
    const inProgress = cases.filter(c => c.status === 'in_progress').length
    const closed = cases.filter(c => c.status === 'closed').length
    followupChartData.value = {
      labels: ['Open', 'In Progress', 'Closed'],
      datasets: [{ data: [open, inProgress, closed], backgroundColor: ['#dc2626', '#f59e0b', '#1a6b3c'], borderWidth: 0 }]
    }

  } catch (e) {
    console.error('Dashboard load error:', e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.event-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--cos-border); }
.event-row:last-child { border-bottom: none; }
.event-date-badge { text-align: center; background: var(--cos-primary-light); color: var(--cos-primary); border-radius: 8px; padding: 4px 10px; min-width: 46px; }
.ev-month { display: block; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }
.ev-day { display: block; font-size: 18px; font-weight: 800; line-height: 1.1; }
.quick-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.qa-btn {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 14px 10px; background: var(--cos-bg); border-radius: 10px;
  color: var(--cos-text); text-decoration: none; font-size: 12px; font-weight: 600;
  transition: all 0.2s; border: 1px solid var(--cos-border);
}
.qa-btn i { font-size: 20px; color: var(--cos-primary); }
.qa-btn:hover { background: var(--cos-primary-light); border-color: var(--cos-primary); color: var(--cos-primary); }
</style>
