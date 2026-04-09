<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Reports</h1><p class="page-subtitle">Generate and export reports for all modules</p></div>
    </div>

    <!-- Summary stats -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3" v-for="s in quickStats" :key="s.label">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: s.bg }"><i :class="`bi ${s.icon}`" :style="{ color: s.color }"></i></div>
          <div><div class="stat-value">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </div>
      </div>
    </div>

    <!-- Report cards -->
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="r in reportTypes" :key="r.id">
        <div class="cos-card report-card h-100">
          <div class="d-flex align-items-start gap-3 mb-3">
            <div class="report-icon" :style="{ background: r.bg }">
              <i :class="`bi ${r.icon}`" :style="{ color: r.color }"></i>
            </div>
            <div>
              <h6 class="fw-bold mb-1">{{ r.title }}</h6>
              <p class="text-muted small mb-0">{{ r.description }}</p>
            </div>
          </div>
          <div class="row g-2 mb-3">
            <div class="col-6">
              <label class="form-label" style="font-size:11px;margin-bottom:3px">From</label>
              <input type="date" class="form-control form-control-sm" v-model="r.from" />
            </div>
            <div class="col-6">
              <label class="form-label" style="font-size:11px;margin-bottom:3px">To</label>
              <input type="date" class="form-control form-control-sm" v-model="r.to" />
            </div>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-primary flex-grow-1" @click="download(r, 'json')" :disabled="r.loading">
              <span v-if="r.loading" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-eye me-1"></i>Preview
            </button>
            <button class="btn btn-sm btn-success flex-grow-1" @click="download(r, 'excel')" :disabled="r.loading">
              <i class="bi bi-file-excel me-1"></i>Excel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview modal -->
    <div class="modal show d-block" v-if="previewData" @click.self="previewData=null">
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ previewTitle }}</h5>
            <button class="btn-close" @click="previewData=null"></button>
          </div>
          <div class="modal-body">
            <div class="table-responsive" v-if="previewRows.length">
              <table class="cos-table">
                <thead>
                  <tr><th v-for="col in previewColumns" :key="col">{{ col }}</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(row, i) in previewRows.slice(0,100)" :key="i">
                    <td v-for="col in previewColumns" :key="col">{{ row[col] }}</td>
                  </tr>
                </tbody>
              </table>
              <p class="text-muted small mt-2" v-if="previewRows.length > 100">
                Showing first 100 of {{ previewRows.length }} records. Download Excel for full data.
              </p>
            </div>
            <div class="cos-empty" v-else><i class="bi bi-inbox"></i><p>No data for selected period.</p></div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop show" v-if="previewData"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import api from '@/api'
import { financeApi, membersApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)

const today = dayjs().format('YYYY-MM-DD')
const firstDay = dayjs().startOf('month').format('YYYY-MM-DD')

const quickStats = ref([
  { label: 'Active Members', value: '—', icon: 'bi-people-fill', bg: '#e8f5ee', color: '#1a6b3c' },
  { label: 'This Month Income', value: '—', icon: 'bi-cash-coin', bg: '#fff3cd', color: '#856404' },
  { label: 'Staff Count', value: '—', icon: 'bi-person-badge', bg: '#dbeafe', color: '#1e40af' },
  { label: 'Inventory Items', value: '—', icon: 'bi-box-seam', bg: '#fce7f3', color: '#9d174d' },
])

const reportTypes = ref([
  {
    id: 'finance', title: 'Financial Report', endpoint: '/reports/finance/',
    description: 'Income, expenses, and net balance. Includes all transaction types.',
    icon: 'bi-cash-coin', bg: '#e8f5ee', color: '#1a6b3c',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'tithes', title: 'Tithe Report', endpoint: '/reports/tithes/',
    description: 'Per-member tithe summary. Ranks givers by total amount.',
    icon: 'bi-journal-check', bg: '#fff3cd', color: '#856404',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'members', title: 'Member Report', endpoint: '/reports/members/',
    description: 'Complete member directory with all contact and membership details.',
    icon: 'bi-people-fill', bg: '#dbeafe', color: '#1e40af',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'attendance', title: 'Attendance Report', endpoint: '/reports/attendance/',
    description: 'Service and event attendance records for the selected period.',
    icon: 'bi-calendar-check', bg: '#fce7f3', color: '#9d174d',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'payroll', title: 'Payroll Report', endpoint: '/reports/payroll/',
    description: 'Staff salary, allowances, deductions, and net pay summary.',
    icon: 'bi-wallet2', bg: '#f3e8ff', color: '#7c3aed',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'inventory', title: 'Inventory Report', endpoint: '/reports/inventory/',
    description: 'Current asset register with condition, value, and custodian details.',
    icon: 'bi-box-seam', bg: '#fef3c7', color: '#b45309',
    from: firstDay, to: today, loading: false,
  },
  {
    id: 'audit', title: 'Audit Report', endpoint: '/reports/audit/',
    description: 'Self-audit results: passed, warnings, and failures with details.',
    icon: 'bi-shield-check', bg: '#fee2e2', color: '#991b1b',
    from: firstDay, to: today, loading: false,
  },
])

const previewData = ref(null)
const previewTitle = ref('')
const previewRows = ref([])
const previewColumns = ref([])

async function download(report, fmt) {
  report.loading = true
  try {
    const params = {
      date_from: report.from,
      date_to: report.to,
      format: fmt,
    }

    if (fmt === 'excel') {
      const response = await api.get(report.endpoint, {
        params,
        responseType: 'blob',
      })
      const url = URL.createObjectURL(response.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${report.id}_report_${report.from}_${report.to}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    } else {
      const { data } = await api.get(report.endpoint, { params })
      previewTitle.value = report.title
      previewData.value = data

      // Extract rows from various response formats
      const rows = data.transactions || data.members || data.records ||
                   data.payslips || data.items || data.reports || []
      previewRows.value = rows
      if (rows.length > 0) {
        previewColumns.value = Object.keys(rows[0])
      } else {
        previewColumns.value = []
      }
    }
  } catch (e) {
    alert('Could not generate report. Please try again.')
    console.error(e)
  } finally {
    report.loading = false
  }
}

async function loadQuickStats() {
  try {
    const [membersRes, financeRes] = await Promise.all([
      membersApi.list({ page_size: 1 }),
      financeApi.summary({ period: 'this_month' }),
    ])
    quickStats.value[0].value = membersRes.data.count || '—'
    quickStats.value[1].value = fmtCur(financeRes.data.this_month || 0)
  } catch {}
  try {
    const { data } = await api.get('/workers/?page_size=1')
    quickStats.value[2].value = data.count || '—'
  } catch {}
  try {
    const { data } = await api.get('/inventory/summary/')
    quickStats.value[3].value = data.total_items || '—'
  } catch {}
}

onMounted(loadQuickStats)
</script>

<style scoped>
.report-card { transition: all .2s; }
.report-card:hover { box-shadow: var(--cos-shadow-lg); transform: translateY(-2px); }
.report-icon { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
</style>
