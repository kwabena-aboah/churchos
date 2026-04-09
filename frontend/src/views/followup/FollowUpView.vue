<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Member Follow-Up</h1><p class="page-subtitle">Pastoral care and member engagement tracker</p></div><button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>New Case</button></div>
    <div class="cos-card mb-3"><div class="row g-2">
      <div class="col-md-3"><select v-model="statusFilter" class="form-select form-select-sm" @change="load"><option value="">All Statuses</option><option value="open">Open</option><option value="in_progress">In Progress</option><option value="closed">Closed</option></select></div>
      <div class="col-md-3"><select v-model="priorityFilter" class="form-select form-select-sm" @change="load"><option value="">All Priorities</option><option value="urgent">Urgent</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option></select></div>
      <div class="col-md-3"><select v-model="typeFilter" class="form-select form-select-sm" @change="load"><option value="">All Types</option><option value="absentee">Absentee</option><option value="new_visitor">New Visitor</option><option value="bereavement">Bereavement</option><option value="illness">Illness</option><option value="spiritual_crisis">Spiritual Crisis</option></select></div>
    </div></div>
    <div class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Member</th><th>Type</th><th>Priority</th><th>Assigned To</th><th>Logs</th><th>Status</th><th>Created</th><th></th></tr></thead>
          <tbody>
            <tr v-for="c in cases" :key="c.id">
              <td><div class="fw-semibold">{{ c.member_name }}</div><div class="text-muted" style="font-size:11px">{{ c.member_phone }}</div></td>
              <td><span class="badge bg-light text-dark border">{{ c.case_type.replace("_"," ") }}</span></td>
              <td><span class="status-badge" :class="priorityClass(c.priority)">{{ c.priority }}</span></td>
              <td>{{ c.assigned_to_name || "Unassigned" }}</td>
              <td>{{ c.log_count }}</td>
              <td><span class="status-badge" :class="c.status==='closed'?'badge-active':c.status==='open'?'badge-inactive':'badge-warning'">{{ c.status.replace("_"," ") }}</span></td>
              <td class="text-muted small">{{ fmt(c.created_at) }}</td>
              <td>
                <button class="btn btn-xs btn-outline-primary me-1" @click="openLogModal(c)">+ Log</button>
                <button class="btn btn-xs btn-success" @click="closeCase(c)" v-if="c.status!=='closed'">Close</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">{{ logModal?"Add Contact Log":"New Follow-Up Case" }}</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body" v-if="!logModal">
        <div class="mb-3"><label class="form-label">Member *</label><input v-model="memberSearch" class="form-control" placeholder="Search…" @input="searchMembers" /><div class="member-dropdown" v-if="memberResults.length"><div v-for="m in memberResults" :key="m.id" class="member-option" @click="selectMember(m)">{{ m.full_name }}</div></div><div v-if="selectedMember" class="text-success small mt-1">{{ selectedMember.full_name }}</div></div>
        <div class="mb-3"><label class="form-label">Case Type</label><select v-model="form.case_type" class="form-select"><option value="absentee">Absentee</option><option value="new_visitor">New Visitor</option><option value="bereavement">Bereavement</option><option value="illness">Illness</option><option value="spiritual_crisis">Spiritual Crisis</option><option value="other">Other</option></select></div>
        <div class="mb-3"><label class="form-label">Priority</label><select v-model="form.priority" class="form-select"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="urgent">Urgent</option></select></div>
        <div class="mb-3"><label class="form-label">Description *</label><textarea v-model="form.description" class="form-control" rows="3" required></textarea></div>
      </div>
      <div class="modal-body" v-else>
        <div class="mb-3"><label class="form-label">Contact Method</label><select v-model="logForm.contact_method" class="form-select"><option value="call">Phone Call</option><option value="visit">Visit</option><option value="message">Message</option><option value="email">Email</option><option value="whatsapp">WhatsApp</option></select></div>
        <div class="mb-3"><label class="form-label">Date</label><input v-model="logForm.contact_date" type="date" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Outcome *</label><textarea v-model="logForm.outcome" class="form-control" rows="3" required></textarea></div>
        <div class="mb-3"><label class="form-label">Next Action</label><input v-model="logForm.next_action" class="form-control" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { followupApi, membersApi } from "@/api"
const fmt = d => dayjs(d).format("DD MMM YYYY")
const priorityClass = p => ({urgent:"badge-inactive",high:"badge-inactive",medium:"badge-warning",low:"badge-visitor"}[p]||"badge-visitor")
const cases=ref([]); const statusFilter=ref(""); const priorityFilter=ref(""); const typeFilter=ref("")
const showModal=ref(false); const logModal=ref(false); const saving=ref(false); const activeCase=ref(null)
const form=ref({case_type:"absentee",priority:"medium",description:""}); const logForm=ref({contact_method:"call",contact_date:dayjs().format("YYYY-MM-DD"),outcome:"",next_action:""})
const memberSearch=ref(""); const memberResults=ref([]); const selectedMember=ref(null)
async function load(){const p={};if(statusFilter.value)p.status=statusFilter.value;if(priorityFilter.value)p.priority=priorityFilter.value;if(typeFilter.value)p.case_type=typeFilter.value;const{data}=await followupApi.list(p);cases.value=data.results||data}
function openModal(){logModal.value=false;selectedMember.value=null;memberSearch.value="";form.value={case_type:"absentee",priority:"medium",description:""};showModal.value=true}
function openLogModal(c){logModal.value=true;activeCase.value=c;logForm.value={contact_method:"call",contact_date:dayjs().format("YYYY-MM-DD"),outcome:"",next_action:""};showModal.value=true}
let t; async function searchMembers(){clearTimeout(t);t=setTimeout(async()=>{if(memberSearch.value.length<2){memberResults.value=[];return};const{data}=await membersApi.list({search:memberSearch.value,page_size:8});memberResults.value=data.results||data},300)}
function selectMember(m){selectedMember.value=m;form.value.member=m.id;memberSearch.value="";memberResults.value=[]}
async function save(){saving.value=true;try{if(logModal.value){await followupApi.addLog(activeCase.value.id,logForm.value)}else{await followupApi.create(form.value)};showModal.value=false;load()}finally{saving.value=false}}
async function closeCase(c){const notes=prompt("Closure notes:");await followupApi.close(c.id,notes||"");load()}
onMounted(load)
</script>
<style scoped>.btn-xs{padding:2px 7px;font-size:11px}.member-dropdown{background:#fff;border:1px solid var(--cos-border);border-radius:8px;max-height:160px;overflow-y:auto}.member-option{padding:8px 12px;cursor:pointer;font-size:13px}.member-option:hover{background:var(--cos-primary-light)}</style>