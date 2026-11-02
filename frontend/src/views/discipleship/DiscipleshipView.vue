<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Discipleship</h1><p class="page-subtitle">Tracks, classes, and member enrollments</p></div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" :class="tab==='tracks'?'active':''" @click="tab='tracks'">Tracks</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='classes'?'active':''" @click="tab='classes'">Classes</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='enrollments'?'active':''" @click="tab='enrollments'">Enrollments</button>
        <button class="btn btn-primary btn-sm" @click="openModal"><i class="bi bi-plus me-1"></i>New</button>
      </div>
    </div>

    <!-- Tracks -->
    <div v-if="tab==='tracks'" class="row g-3">
      <div class="col-md-4" v-for="t in tracks" :key="t.id">
        <div class="cos-card">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h6 class="fw-bold mb-0">{{ t.name }}</h6>
            <span class="badge bg-primary-subtle text-primary">Track {{ t.order }}</span>
          </div>
          <p class="text-muted small mb-2">{{ t.description || 'No description' }}</p>
          <div class="text-muted small" v-if="t.duration_weeks">
            <i class="bi bi-clock me-1"></i>{{ t.duration_weeks }} weeks
          </div>
        </div>
      </div>
      <div class="col-12" v-if="tracks.length===0">
        <div class="cos-card cos-empty"><i class="bi bi-book"></i><p>No tracks created yet.</p></div>
      </div>
    </div>

    <!-- Classes -->
    <div v-if="tab==='classes'" class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Class</th><th>Track</th><th>Facilitator</th><th>Start Date</th><th>End Date</th><th>Enrolled</th></tr></thead>
          <tbody>
            <tr v-for="c in classes" :key="c.id">
              <td class="fw-semibold">{{ c.name }}</td>
              <td>{{ c.track_name }}</td>
              <td>{{ c.facilitator || '—' }}</td>
              <td>{{ fmt(c.start_date) }}</td>
              <td>{{ c.end_date ? fmt(c.end_date) : 'Ongoing' }}</td>
              <td><span class="badge bg-primary-subtle text-primary">{{ c.enrollment_count }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Enrollments -->
    <div v-if="tab==='enrollments'" class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Member</th><th>Class</th><th>Status</th><th>Enrolled</th><th>Completed</th><th>Certificate</th></tr></thead>
          <tbody>
            <tr v-for="e in enrollments" :key="e.id">
              <td class="fw-semibold">{{ e.member_name }}</td>
              <td>{{ e.class_name }}</td>
              <td><span class="status-badge" :class="e.status==='completed'?'badge-active':e.status==='dropped'?'badge-inactive':'badge-visitor'">{{ e.status }}</span></td>
              <td>{{ fmt(e.enrolled_at) }}</td>
              <td>{{ e.completed_at ? fmt(e.completed_at) : '—' }}</td>
              <td><i :class="`bi ${e.certificate_issued ? 'bi-patch-check-fill text-success' : 'bi-patch-check text-muted'}`"></i></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog"><div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ tab==='tracks' ? 'New Track' : tab==='classes' ? 'New Class' : 'Enroll Member' }}</h5>
          <button class="btn-close" @click="showModal=false"></button>
        </div>
        <div class="modal-body">
          <!-- Track form -->
          <template v-if="tab==='tracks'">
            <div class="mb-3"><label class="form-label">Track Name *</label><input v-model="form.name" class="form-control" required /></div>
            <div class="mb-3"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
            <div class="row g-2">
              <div class="col-6"><label class="form-label">Order</label><input v-model="form.order" type="number" class="form-control" /></div>
              <div class="col-6"><label class="form-label">Duration (weeks)</label><input v-model="form.duration_weeks" type="number" class="form-control" /></div>
            </div>
          </template>
          <!-- Class form -->
          <template v-if="tab==='classes'">
            <div class="mb-3"><label class="form-label">Class Name *</label><input v-model="form.name" class="form-control" required /></div>
            <div class="mb-3"><label class="form-label">Track *</label><select v-model="form.track" class="form-select"><option v-for="t in tracks" :key="t.id" :value="t.id">{{ t.name }}</option></select></div>
            <div class="row g-2">
              <div class="col-6"><label class="form-label">Start Date *</label><input v-model="form.start_date" type="date" class="form-control" required /></div>
              <div class="col-6"><label class="form-label">End Date</label><input v-model="form.end_date" type="date" class="form-control" /></div>
            </div>
            <div class="mb-3 mt-3"><label class="form-label">Venue</label><input v-model="form.venue" class="form-control" /></div>
          </template>
          <!-- Enrollment form -->
          <template v-if="tab==='enrollments'">
            <div class="mb-3">
              <label class="form-label">Search Member *</label>
              <input v-model="memberSearch" class="form-control" placeholder="Type name…" @input="searchMembers" />
              <div class="member-dropdown" v-if="memberResults.length">
                <div v-for="m in memberResults" :key="m.id" class="member-option" @click="selectMember(m)">{{ m.full_name }} — {{ m.member_number }}</div>
              </div>
              <div v-if="selectedMember" class="text-success small mt-1"><i class="bi bi-check2 me-1"></i>{{ selectedMember.full_name }}</div>
            </div>
            <div class="mb-3"><label class="form-label">Class *</label><select v-model="form.discipleship_class" class="form-select"><option v-for="c in classes" :key="c.id" :value="c.id">{{ c.name }}</option></select></div>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button>
          <button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button>
        </div>
      </div></div>
    </div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import api from '@/api'
import { membersApi } from '@/api'

const tab = ref('tracks')
const tracks = ref([])
const classes = ref([])
const enrollments = ref([])
const showModal = ref(false)
const saving = ref(false)
const form = ref({})
const memberSearch = ref('')
const memberResults = ref([])
const selectedMember = ref(null)

const fmt = d => d ? dayjs(d).format('DD MMM YYYY') : '—'

async function load() {
  if (tab.value === 'tracks') {
    const { data } = await api.get('/discipleship/tracks/')
    tracks.value = data.results || data
  } else if (tab.value === 'classes') {
    const { data } = await api.get('/discipleship/classes/')
    classes.value = data.results || data
  } else {
    const { data } = await api.get('/discipleship/enrollments/?page_size=100')
    enrollments.value = data.results || data
  }
}

watch(tab, load)

function openModal() {
  form.value = {}
  selectedMember.value = null
  memberSearch.value = ''
  showModal.value = true
}

let t
async function searchMembers() {
  clearTimeout(t)
  t = setTimeout(async () => {
    if (memberSearch.value.length < 2) { memberResults.value = []; return }
    const { data } = await membersApi.list({ search: memberSearch.value, page_size: 8 })
    memberResults.value = data.results || data
  }, 300)
}

function selectMember(m) {
  selectedMember.value = m
  form.value.member = m.id
  memberSearch.value = ''
  memberResults.value = []
}

async function save() {
  saving.value = true
  try {
    if (tab.value === 'tracks') {
      await api.post('/discipleship/tracks/', form.value)
    } else if (tab.value === 'classes') {
      await api.post('/discipleship/classes/', form.value)
    } else {
      await api.post('/discipleship/enrollments/', form.value)
    }
    showModal.value = false
    load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.member-dropdown { background:#fff; border:1px solid var(--cos-border); border-radius:8px; max-height:160px; overflow-y:auto; }
.member-option { padding:8px 12px; cursor:pointer; font-size:13px; }
.member-option:hover { background:var(--cos-primary-light); }
</style>
