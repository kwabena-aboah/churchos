<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Finance</h1><p class="page-subtitle">Transactions, giving, and financial records</p></div>
      <div class="d-flex gap-2">
        <select v-model="filters.period" class="form-select form-select-sm" @change="loadData" style="width:140px">
          <option value="this_month">This Month</option>
          <option value="last_month">Last Month</option>
          <option value="this_year">This Year</option>
          <option value="all">All Time</option>
        </select>
        <RouterLink to="/finance/new" class="btn btn-primary btn-sm"><i class="bi bi-plus me-1"></i>Record Giving</RouterLink>
      </div>
    </div>

    <!-- Summary cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3" v-for="s in summaryCards" :key="s.label">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: s.bg }"><i :class="`bi ${s.icon}`" :style="{ color: s.color }"></i></div>
          <div><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="cos-card mb-3">
      <div class="row g-2">
        <div class="col-md-3">
          <input v-model="filters.search" type="text" class="form-control form-control-sm" placeholder="Search reference, member…" @input="debouncedLoad" />
        </div>
        <div class="col-md-2">
          <select v-model="filters.transaction_type" class="form-select form-select-sm" @change="loadTransactions">
            <option value="">All Types</option>
            <option value="tithe">Tithe</option>
            <option value="offering">Offering</option>
            <option value="donation">Donation</option>
            <option value="expense">Expense</option>
            <option value="pledge_payment">Pledge Payment</option>
          </select>
        </div>
        <div class="col-md-2">
          <input v-model="filters.date_from" type="date" class="form-control form-control-sm" @change="loadTransactions" placeholder="From" />
        </div>
        <div class="col-md-2">
          <input v-model="filters.date_to" type="date" class="form-control form-control-sm" @change="loadTransactions" placeholder="To" />
        </div>
        <div class="col-md-2">
          <select v-model="filters.verified" class="form-select form-select-sm" @change="loadTransactions">
            <option value="">All</option>
            <option value="true">Verified</option>
            <option value="false">Unverified</option>
          </select>
        </div>
        <div class="col-md-1">
          <button class="btn btn-sm btn-outline-secondary w-100" @click="clearFilters"><i class="bi bi-x"></i></button>
        </div>
      </div>
    </div>

    <!-- Transactions table -->
    <div class="cos-card p-0">
      <div v-if="loading" class="cos-spinner p-5"><div class="spinner-border text-primary"></div></div>
      <div v-else-if="transactions.length === 0" class="cos-empty p-5">
        <i class="bi bi-receipt"></i><p>No transactions found</p>
      </div>
      <div v-else class="table-responsive">
        <table class="cos-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Reference</th>
              <th>Member</th>
              <th>Type</th>
              <th>Payment</th>
              <th>Amount</th>
              <th>Verified</th>
              <th>Recorded By</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in transactions" :key="t.id">
              <td>{{ formatDate(t.transaction_date) }}</td>
              <td><code class="text-primary small">{{ t.reference }}</code></td>
              <td>{{ t.member_name }}</td>
              <td>
                <span class="status-badge" :class="typeClass(t.transaction_type)">{{ t.transaction_type.replace('_',' ') }}</span>
              </td>
              <td><span class="text-muted small">{{ t.payment_method?.replace('_',' ') }}</span></td>
              <td>
                <span :class="t.transaction_type === 'expense' ? 'text-danger fw-bold' : 'text-success fw-bold'">
                  {{ t.transaction_type === 'expense' ? '-' : '+' }}{{ fmtCur(t.amount) }}
                </span>
              </td>
              <td>
                <i :class="`bi ${t.verified ? 'bi-check-circle-fill text-success' : 'bi-clock text-warning'}`"></i>
              </td>
              <td class="text-muted small">{{ t.recorded_by_name }}</td>
              <td>
                <button class="btn btn-xs btn-outline-secondary" @click="downloadReceipt(t.id)" title="Receipt">
                  <i class="bi bi-receipt"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div class="d-flex align-items-center justify-content-between p-3 border-top" v-if="pagination.total_pages > 1">
        <span class="text-muted small">{{ pagination.count }} transactions</span>
        <div class="d-flex gap-1">
          <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.previous" @click="goPage(pagination.current_page-1)"><i class="bi bi-chevron-left"></i></button>
          <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.next" @click="goPage(pagination.current_page+1)"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { financeApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const transactions = ref([])
const loading = ref(false)
const filters = ref({ search: '', transaction_type: '', date_from: '', date_to: '', verified: '', period: 'this_month' })
const pagination = ref({ count: 0, total_pages: 1, current_page: 1, next: null, previous: null })

const summaryCards = ref([
  { label: 'Total Tithes',   value: '—', icon: 'bi-cash', bg: '#e8f5ee', color: '#1a6b3c' },
  { label: 'Total Offerings',value: '—', icon: 'bi-collection', bg: '#fff3cd', color: '#856404' },
  { label: 'Total Donations',value: '—', icon: 'bi-heart', bg: '#fce7f3', color: '#9d174d' },
  { label: 'Total Expenses', value: '—', icon: 'bi-arrow-up-circle', bg: '#fee2e2', color: '#991b1b' },
])

const fmtCur = (v) => settingsStore.formatCurrency(v)
const formatDate = (d) => dayjs(d).format('DD MMM YYYY')
function typeClass(t) {
  return { tithe: 'badge-active', offering: 'badge-visitor', donation: 'badge-warning', expense: 'badge-inactive', pledge_payment: 'badge-info' }[t] || 'badge-visitor'
}

let debounceTimer
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(loadTransactions, 400) }

async function loadData() {
  await Promise.all([loadTransactions(), loadSummary()])
}

async function loadSummary() {
  try {
    const { data } = await financeApi.summary({ period: filters.value.period })
    summaryCards.value[0].value = fmtCur(data.total_tithes || 0)
    summaryCards.value[1].value = fmtCur(data.total_offerings || 0)
    summaryCards.value[2].value = fmtCur(data.total_donations || 0)
    summaryCards.value[3].value = fmtCur(data.total_expenses || 0)
  } catch {}
}

async function loadTransactions(page = 1) {
  loading.value = true
  try {
    const params = { page, page_size: 25 }
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.transaction_type) params.transaction_type = filters.value.transaction_type
    if (filters.value.date_from) params.transaction_date__gte = filters.value.date_from
    if (filters.value.date_to) params.transaction_date__lte = filters.value.date_to
    if (filters.value.verified) params.verified = filters.value.verified
    const { data } = await financeApi.listTransactions(params)
    transactions.value = data.results || data
    if (data.count !== undefined) pagination.value = { count: data.count, total_pages: data.total_pages, current_page: data.current_page, next: data.next, previous: data.previous }
  } finally { loading.value = false }
}

function goPage(p) { if (p >= 1) loadTransactions(p) }
function clearFilters() { filters.value = { search: '', transaction_type: '', date_from: '', date_to: '', verified: '', period: 'this_month' }; loadData() }

async function downloadReceipt(id) {
  try {
    const { data } = await financeApi.downloadReceipt(id)
    const url = URL.createObjectURL(data)
    const a = document.createElement('a'); a.href = url; a.download = `receipt-${id}.pdf`; a.click()
    URL.revokeObjectURL(url)
  } catch { alert('Receipt not available.') }
}

onMounted(loadData)
</script>
