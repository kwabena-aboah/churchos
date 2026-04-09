<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Payroll</h1><p class="page-subtitle">Monthly payroll runs and payslips</p></div>
      <button class="btn btn-primary btn-sm" @click="openCreate"><i class="bi bi-plus me-1"></i>New Payroll Run</button>
    </div>
    <div class="row g-3">
      <div class="col-md-4" v-for="run in runs" :key="run.id">
        <div class="cos-card">
          <div class="d-flex justify-content-between mb-2">
            <h6 class="fw-bold mb-0">{{ monthName(run.month) }} {{ run.year }}</h6>
            <span class="status-badge" :class="run.status==='paid'?'badge-active':run.status==='approved'?'badge-visitor':'badge-warning'">{{ run.status }}</span>
          </div>
          <div class="row text-center my-3">
            <div class="col-4"><div class="text-muted small">Gross</div><div class="fw-bold">{{ fmtCur(run.total_gross) }}</div></div>
            <div class="col-4"><div class="text-muted small">Deductions</div><div class="fw-bold text-danger">{{ fmtCur(run.total_deductions) }}</div></div>
            <div class="col-4"><div class="text-muted small">Net</div><div class="fw-bold text-success">{{ fmtCur(run.total_net) }}</div></div>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary flex-grow-1" @click="generatePayroll(run)" :disabled="run.status!=='draft'"><i class="bi bi-gear me-1"></i>Generate</button>
            <button class="btn btn-sm btn-success flex-grow-1" @click="approvePayroll(run)" :disabled="run.status!=='draft'"><i class="bi bi-check2 me-1"></i>Approve</button>
          </div>
        </div>
      </div>
      <div class="col-12" v-if="runs.length===0&&!loading"><div class="cos-card cos-empty"><i class="bi bi-wallet2"></i><p>No payroll runs yet.</p></div></div>
    </div>

    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">New Payroll Run</h5><button class="btn-close" @click="showModal=false"></button></div>
          <div class="modal-body">
            <div class="mb-3"><label class="form-label">Month *</label><select v-model="form.month" class="form-select"><option v-for="i in 12" :key="i" :value="i">{{ monthName(i) }}</option></select></div>
            <div class="mb-3"><label class="form-label">Year *</label><input v-model="form.year" type="number" class="form-control" /></div>
            <div class="mb-3"><label class="form-label">Notes</label><textarea v-model="form.notes" class="form-control" rows="2"></textarea></div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="createRun" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Create</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { workersApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const monthName = m => dayjs().month(m-1).format('MMMM')
const runs = ref([]); const loading = ref(false); const showModal = ref(false); const saving = ref(false)
const form = ref({ month: dayjs().month()+1, year: dayjs().year(), notes:'' })
async function load() { loading.value=true; const {data}=await workersApi.getPayrollRuns(); runs.value=data.results||data; loading.value=false }
function openCreate() { form.value={month:dayjs().month()+1,year:dayjs().year(),notes:''}; showModal.value=true }
async function createRun() { saving.value=true; try { await workersApi.createPayrollRun(form.value); showModal.value=false; load() } finally { saving.value=false } }
async function generatePayroll(run) { if(!confirm('Generate payslips for all active workers?')) return; await workersApi.generatePayroll(run.id); load(); alert('Payslips generated.') }
async function approvePayroll(run) { if(!confirm('Approve this payroll run?')) return; await workersApi.approvePayroll(run.id); load() }
onMounted(load)
</script>
