<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Leave Requests</h1></div><button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>Request Leave</button></div>
    <div class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead>
            <tr>
              <th>Worker</th>
              <th>Type</th>
              <th>From</th>
              <th>To</th>
              <th>Days</th>
              <th>Reason</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in leaves" :key="l.id">
              <td class="fw-semibold">{{ l.worker_name }}</td>
              <td><span class="badge bg-light text-dark border">{{ l.leave_type }}</span></td>
              <td>{{ fmt(l.start_date) }}</td><td>{{ fmt(l.end_date) }}</td>
              <td>{{ l.days_requested }}</td>
              <td class="text-muted small">{{ l.reason || "—" }}</td>
              <td><span class="status-badge" :class="l.status==='approved'?'badge-active':l.status==='rejected'?'badge-inactive':'badge-warning'">{{ l.status }}</span></td>
              <td>
                <button v-if="l.status==='pending'" class="btn btn-xs btn-success me-1" @click="approve(l.id)"><i class="bi bi-check2"></i></button>
                <button v-if="l.status==='pending'" class="btn btn-xs btn-danger" @click="reject(l.id)"><i class="bi bi-x"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Request Leave</h5><button class="btn-close" @click="showModal=false"></button></div>
        <div class="modal-body">
          <div class="mb-3"><label class="form-label">Worker *</label><select v-model="form.worker" class="form-select"><option :value="null">Select</option><option v-for="w in workers" :key="w.id" :value="w.id">{{ w.full_name }}</option></select></div>
          <div class="mb-3"><label class="form-label">Leave Type</label><select v-model="form.leave_type" class="form-select"><option value="annual">Annual</option><option value="sick">Sick</option><option value="maternity">Maternity</option><option value="paternity">Paternity</option><option value="unpaid">Unpaid</option><option value="compassionate">Compassionate</option></select></div>
          <div class="row g-2 mb-3"><div class="col-6"><label class="form-label">From</label><input v-model="form.start_date" type="date" class="form-control" /></div><div class="col-6"><label class="form-label">To</label><input v-model="form.end_date" type="date" class="form-control" /></div></div>
          <div class="mb-3"><label class="form-label">Days</label><input v-model="form.days_requested" type="number" class="form-control" /></div>
          <div class="mb-3"><label class="form-label">Reason</label><textarea v-model="form.reason" class="form-control" rows="2"></textarea></div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Submit</button></div>
      </div></div>
    </div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { workersApi } from "@/api"
const leaves = ref([]); const workers = ref([]); const showModal = ref(false); const saving = ref(false)
const form = ref({ worker: null, leave_type: "annual", start_date: "", end_date: "", days_requested: 1, reason: "" })
const fmt = d => dayjs(d).format("DD MMM YYYY")
async function load() { const { data } = await workersApi.getLeaveRequests(); leaves.value = data.results || data }
function openModal() { form.value = { worker: null, leave_type: "annual", start_date: "", end_date: "", days_requested: 1, reason: "" }; showModal.value = true }
async function save() { saving.value = true; try { await workersApi.createLeaveRequest(form.value); showModal.value = false; load() } finally { saving.value = false } }
async function approve(id) { await workersApi.approveLeave(id); load() }
async function reject(id) { const reason = prompt("Rejection reason:"); await workersApi.rejectLeave(id, reason); load() }
onMounted(async () => { const { data } = await workersApi.list({ page_size: 200 }); workers.value = data.results || data; load() })
</script>