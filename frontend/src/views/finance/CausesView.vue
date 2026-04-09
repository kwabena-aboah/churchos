<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Causes & Projects</h1><p class="page-subtitle">Track fundraising goals and progress</p></div>
      <button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>New Cause</button>
    </div>
    <div class="row g-3">
      <div class="col-md-4" v-for="c in causes" :key="c.id">
        <div class="cos-card">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h6 class="fw-bold mb-0">{{ c.name }}</h6>
            <span class="status-badge" :class="c.is_active ? 'badge-active' : 'badge-inactive'">{{ c.is_active ? 'Active' : 'Closed' }}</span>
          </div>
          <p class="text-muted small mb-3">{{ c.description || 'No description' }}</p>
          <div v-if="c.target_amount">
            <div class="d-flex justify-content-between small mb-1">
              <span>{{ fmtCur(c.total_raised) }} raised</span>
              <span class="fw-bold">{{ c.progress_percent }}%</span>
            </div>
            <div class="progress" style="height:8px">
              <div class="progress-bar bg-success" :style="{ width: `${Math.min(c.progress_percent,100)}%` }"></div>
            </div>
            <div class="text-muted small mt-1">Goal: {{ fmtCur(c.target_amount) }}</div>
          </div>
          <div v-else class="text-muted small">Total raised: {{ fmtCur(c.total_raised) }}</div>
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-sm btn-outline-primary flex-grow-1" @click="openModal(c)"><i class="bi bi-pencil me-1"></i>Edit</button>
          </div>
        </div>
      </div>
      <div class="col-12" v-if="causes.length === 0 && !loading">
        <div class="cos-card cos-empty"><i class="bi bi-heart"></i><p>No causes yet. Create your first fundraising cause.</p></div>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">{{ editing ? 'Edit Cause' : 'New Cause' }}</h5><button class="btn-close" @click="showModal=false"></button></div>
          <div class="modal-body">
            <div class="mb-3"><label class="form-label">Name *</label><input v-model="form.name" class="form-control" required /></div>
            <div class="mb-3"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
            <div class="mb-3"><label class="form-label">Target Amount</label><input v-model="form.target_amount" type="number" step="0.01" class="form-control" /></div>
            <div class="row g-2">
              <div class="col-6"><label class="form-label">Start Date</label><input v-model="form.start_date" type="date" class="form-control" /></div>
              <div class="col-6"><label class="form-label">End Date</label><input v-model="form.end_date" type="date" class="form-control" /></div>
            </div>
            <div class="form-check mt-3"><input class="form-check-input" type="checkbox" v-model="form.is_ongoing" id="ongoing" /><label class="form-check-label" for="ongoing">Ongoing (no end date)</label></div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="saveCause" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save
            </button>
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
import { financeApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const causes = ref([])
const loading = ref(false)
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const form = ref({ name:'', description:'', target_amount:'', start_date:dayjs().format('YYYY-MM-DD'), end_date:'', is_ongoing:false })

async function load() { loading.value=true; const {data}=await financeApi.getCauses(); causes.value=data.results||data; loading.value=false }
function openModal(c=null) { editing.value=c; form.value=c?{...c}:{name:'',description:'',target_amount:'',start_date:dayjs().format('YYYY-MM-DD'),end_date:'',is_ongoing:false}; showModal.value=true }
async function saveCause() {
  saving.value=true
  try { editing.value ? await financeApi.updateCause(editing.value.id,form.value) : await financeApi.createCause(form.value); showModal.value=false; load() }
  finally { saving.value=false }
}
onMounted(load)
</script>
