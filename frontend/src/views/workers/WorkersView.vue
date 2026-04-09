<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Workers</h1><p class="page-subtitle">{{ workers.length }} staff records</p></div>
      <button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-person-plus me-1"></i>Add Worker</button>
    </div>
    <div class="cos-card mb-3">
      <div class="row g-2">
        <div class="col-md-4"><input v-model="search" type="text" class="form-control form-control-sm" placeholder="Search name, role…" @input="debouncedLoad" /></div>
        <div class="col-md-3"><select v-model="filters.department" class="form-select form-select-sm" @change="loadWorkers"><option value="">All Departments</option><option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option></select></div>
        <div class="col-md-3"><select v-model="filters.employment_status" class="form-select form-select-sm" @change="loadWorkers"><option value="">All Statuses</option><option value="active">Active</option><option value="on_leave">On Leave</option><option value="terminated">Terminated</option></select></div>
      </div>
    </div>
    <div class="cos-card p-0">
      <div v-if="loading" class="cos-spinner p-4"><div class="spinner-border text-primary"></div></div>
      <div class="table-responsive" v-else>
        <table class="cos-table">
          <thead>
            <tr>
              <th>Worker</th>
              <th>Employee ID</th>
              <th>Role</th>
              <th>Department</th>
              <th>Type</th>
              <th>Basic Salary</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="w in workers" :key="w.id">
              <td><div class="d-flex align-items-center gap-2"><div class="member-avatar">{{ initials(w.full_name) }}</div><span class="fw-semibold">{{ w.full_name }}</span></div></td>
              <td><code class="text-primary">{{ w.employee_id }}</code></td>
              <td>{{ w.job_title }}</td>
              <td>{{ w.department_name || '—' }}</td>
              <td><span class="badge bg-light text-dark border">{{ w.employment_type.replace('_',' ') }}</span></td>
              <td class="fw-semibold">{{ fmtCur(w.basic_salary) }}</td>
              <td><span class="status-badge" :class="w.employment_status==='active'?'badge-active':w.employment_status==='on_leave'?'badge-warning':'badge-inactive'">{{ w.employment_status.replace('_',' ') }}</span></td>
              <td><button class="btn btn-xs btn-outline-primary" @click="openModal(w)"><i class="bi bi-pencil"></i></button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editing ? 'Edit Worker' : 'Add Worker' }}</h5><button class="btn-close" @click="showModal=false"></button></div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-4"><label class="form-label">First Name *</label><input v-model="form.first_name" class="form-control" required /></div>
              <div class="col-md-4"><label class="form-label">Last Name *</label><input v-model="form.last_name" class="form-control" required /></div>
              <div class="col-md-4"><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Job Title *</label><input v-model="form.job_title" class="form-control" required /></div>
              <div class="col-md-4"><label class="form-label">Department</label><select v-model="form.department" class="form-select"><option :value="null">None</option><option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option></select></div>
              <div class="col-md-4"><label class="form-label">Employment Type</label><select v-model="form.employment_type" class="form-select"><option value="full_time">Full-Time</option><option value="part_time">Part-Time</option><option value="contract">Contract</option><option value="volunteer">Volunteer</option></select></div>
              <div class="col-md-4"><label class="form-label">Start Date *</label><input v-model="form.start_date" type="date" class="form-control" required /></div>
              <div class="col-md-4"><label class="form-label">Basic Salary</label><input v-model="form.basic_salary" type="number" step="0.01" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Bank Name</label><input v-model="form.bank_name" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Bank Account No.</label><input v-model="form.bank_account_number" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Mobile Money No.</label><input v-model="form.mobile_money_number" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">SSNIT Number</label><input v-model="form.ssnit_number" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">TIN Number</label><input v-model="form.tin_number" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Status</label><select v-model="form.employment_status" class="form-select"><option value="active">Active</option><option value="on_leave">On Leave</option><option value="suspended">Suspended</option><option value="terminated">Terminated</option></select></div>
              <div class="col-12"><label class="form-label">Notes</label><textarea v-model="form.notes" class="form-control" rows="2"></textarea></div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="saveWorker" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button>
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
const initials = n => n?.split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2)||'?'
const workers = ref([]); const departments = ref([]); const loading = ref(false)
const search = ref(''); const filters = ref({ department:'', employment_status:'' })
const showModal = ref(false); const editing = ref(null); const saving = ref(false)
const form = ref({ first_name:'',last_name:'',email:'',phone:'',job_title:'',department:null,employment_type:'full_time',start_date:dayjs().format('YYYY-MM-DD'),basic_salary:0,bank_name:'',bank_account_number:'',mobile_money_number:'',ssnit_number:'',tin_number:'',employment_status:'active',notes:'' })

let dt; function debouncedLoad() { clearTimeout(dt); dt=setTimeout(loadWorkers,400) }
async function loadWorkers() { loading.value=true; const p={search:search.value,...Object.fromEntries(Object.entries(filters.value).filter(([,v])=>v))}; const {data}=await workersApi.list(p); workers.value=data.results||data; loading.value=false }
function openModal(w=null) { editing.value=w; form.value=w?{...w}:{first_name:'',last_name:'',email:'',phone:'',job_title:'',department:null,employment_type:'full_time',start_date:dayjs().format('YYYY-MM-DD'),basic_salary:0,bank_name:'',bank_account_number:'',mobile_money_number:'',ssnit_number:'',tin_number:'',employment_status:'active',notes:''}; showModal.value=true }
async function saveWorker() { saving.value=true; try { editing.value?await workersApi.update(editing.value.id,form.value):await workersApi.create(form.value); showModal.value=false; loadWorkers() } finally { saving.value=false } }
onMounted(async()=>{ const {data}=await workersApi.getDepartments(); departments.value=data.results||data; loadWorkers() })
</script>
<style scoped>.member-avatar{width:36px;height:36px;border-radius:50%;background:var(--cos-primary-light);color:var(--cos-primary);font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;flex-shrink:0}.btn-xs{padding:2px 7px;font-size:11px}</style>
