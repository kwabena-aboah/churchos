<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Pledges</h1><p class="page-subtitle">Track member giving commitments</p></div>
      <button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>New Pledge</button>
    </div>
    <div class="cos-card p-0">
      <div v-if="loading" class="cos-spinner p-4"><div class="spinner-border text-primary"></div></div>
      <div class="table-responsive" v-else>
        <table class="cos-table">
          <thead><tr><th>Member</th><th>Cause</th><th>Pledge Amount</th><th>Paid</th><th>Balance</th><th>Due Date</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="p in pledges" :key="p.id">
              <td class="fw-semibold">{{ p.member_name }}</td>
              <td>{{ p.cause_name || '—' }}</td>
              <td>{{ fmtCur(p.pledge_amount) }}</td>
              <td class="text-success">{{ fmtCur(p.amount_paid) }}</td>
              <td :class="p.balance_remaining > 0 ? 'text-danger fw-bold' : 'text-muted'">{{ fmtCur(p.balance_remaining) }}</td>
              <td>{{ p.due_date ? formatDate(p.due_date) : '—' }}</td>
              <td><span class="status-badge" :class="p.is_fulfilled ? 'badge-active' : 'badge-pending'">{{ p.is_fulfilled ? 'Fulfilled' : 'Pending' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header"><h5 class="modal-title">New Pledge</h5><button class="btn-close" @click="showModal=false"></button></div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Member *</label>
              <input v-model="memberSearch" type="text" class="form-control" placeholder="Search member…" @input="searchMembers" />
              <div class="member-dropdown" v-if="memberResults.length">
                <div v-for="m in memberResults" :key="m.id" class="member-option" @click="selectMember(m)">{{ m.full_name }} — {{ m.member_number }}</div>
              </div>
              <div v-if="selectedMember" class="mt-1 text-success small"><i class="bi bi-check2 me-1"></i>{{ selectedMember.full_name }}</div>
            </div>
            <div class="mb-3"><label class="form-label">Cause</label><select v-model="form.cause" class="form-select"><option :value="null">None</option><option v-for="c in causes" :key="c.id" :value="c.id">{{ c.name }}</option></select></div>
            <div class="mb-3"><label class="form-label">Pledge Amount *</label><input v-model="form.pledge_amount" type="number" step="0.01" class="form-control" required /></div>
            <div class="mb-3"><label class="form-label">Due Date</label><input v-model="form.due_date" type="date" class="form-control" /></div>
            <div class="mb-3"><label class="form-label">Notes</label><textarea v-model="form.notes" class="form-control" rows="2"></textarea></div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="savePledge" :disabled="saving || !selectedMember">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save Pledge
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
import { financeApi, membersApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const formatDate = d => dayjs(d).format('DD MMM YYYY')
const pledges = ref([]); const causes = ref([]); const loading = ref(false)
const showModal = ref(false); const saving = ref(false)
const memberSearch = ref(''); const memberResults = ref([]); const selectedMember = ref(null)
const form = ref({ cause: null, pledge_amount: '', due_date: '', notes: '' })

async function load() { loading.value=true; const {data}=await financeApi.getPledges(); pledges.value=data.results||data; loading.value=false }
function openModal() { form.value={cause:null,pledge_amount:'',due_date:'',notes:''}; selectedMember.value=null; memberSearch.value=''; showModal.value=true }
let t; async function searchMembers() { clearTimeout(t); t=setTimeout(async()=>{ if(memberSearch.value.length<2){memberResults.value=[];return}; const {data}=await membersApi.list({search:memberSearch.value,page_size:8}); memberResults.value=data.results||data },300) }
function selectMember(m) { selectedMember.value=m; form.value.member=m.id; memberSearch.value=''; memberResults.value=[] }
async function savePledge() { saving.value=true; try { await financeApi.createPledge({...form.value,member:selectedMember.value.id}); showModal.value=false; load() } finally { saving.value=false } }
onMounted(async()=>{ load(); const {data}=await financeApi.getCauses(); causes.value=data.results||data })
</script>
<style scoped>
.member-dropdown{position:absolute;background:#fff;border:1px solid var(--cos-border);border-radius:8px;z-index:100;max-height:180px;overflow-y:auto;box-shadow:var(--cos-shadow-lg);width:100%}
.member-option{padding:8px 14px;cursor:pointer;font-size:13px}.member-option:hover{background:var(--cos-primary-light)}
</style>
