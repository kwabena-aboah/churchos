<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Communication</h1></div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" :class="tab==='broadcasts'?'active':''" @click="tab='broadcasts'">Broadcasts</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='logs'?'active':''" @click="tab='logs'">Message Log</button>
        <button class="btn btn-primary btn-sm" @click="openBroadcastModal"><i class="bi bi-megaphone me-1"></i>New Broadcast</button>
      </div>
    </div>
    <div v-if="tab==='broadcasts'">
      <div class="row g-3">
        <div class="col-md-6 col-lg-4" v-for="b in broadcasts" :key="b.id">
          <div class="cos-card">
            <div class="d-flex justify-content-between mb-2"><h6 class="fw-bold mb-0">{{ b.title }}</h6><span class="status-badge" :class="b.status==='sent'?'badge-active':'badge-warning'">{{ b.status }}</span></div>
            <p class="text-muted small mb-2">{{ b.body.slice(0,100) }}{{ b.body.length>100?"…":"" }}</p>
            <div class="small text-muted mb-3"><span v-for="ch in b.channels" :key="ch" class="badge bg-light text-dark border me-1">{{ ch }}</span><span class="ms-2">→ {{ b.target_group.replace("_"," ") }}</span></div>
            <div v-if="b.status!=='sent'"><button class="btn btn-sm btn-success w-100" @click="send(b.id)"><i class="bi bi-send me-1"></i>Send Now</button></div>
            <div v-else class="text-muted small"><i class="bi bi-check2-all text-success me-1"></i>Sent to {{ b.recipient_count }} recipients</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="tab==='logs'" class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Date</th><th>Channel</th><th>Recipient</th><th>Event</th><th>Status</th><th></th></tr></thead>
          <tbody>
            <tr v-for="l in logs" :key="l.id">
              <td class="text-muted small">{{ fmt(l.created_at) }}</td>
              <td><span class="badge" :class="l.channel==='email'?'bg-primary':l.channel==='sms'?'bg-success':'bg-success-subtle text-success'">{{ l.channel }}</span></td>
              <td>{{ l.recipient }}</td>
              <td class="text-muted small">{{ l.event_type }}</td>
              <td><span class="status-badge" :class="l.status==='delivered'||l.status==='sent'?'badge-active':l.status==='failed'?'badge-inactive':'badge-warning'">{{ l.status }}</span></td>
              <td><button v-if="l.status==='failed'" class="btn btn-xs btn-outline-warning" @click="retry(l.id)">Retry</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog modal-lg"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">New Broadcast</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body">
        <div class="mb-3"><label class="form-label">Title *</label><input v-model="form.title" class="form-control" required /></div>
        <div class="mb-3"><label class="form-label">Channels</label><div class="d-flex gap-3"><div class="form-check"><input class="form-check-input" type="checkbox" value="email" v-model="form.channels" id="email"><label class="form-check-label" for="email">Email</label></div><div class="form-check"><input class="form-check-input" type="checkbox" value="sms" v-model="form.channels" id="sms"><label class="form-check-label" for="sms">SMS</label></div><div class="form-check"><input class="form-check-input" type="checkbox" value="whatsapp" v-model="form.channels" id="wa"><label class="form-check-label" for="wa">WhatsApp</label></div></div></div>
        <div class="mb-3"><label class="form-label">Target Group</label><select v-model="form.target_group" class="form-select"><option value="all_active">All Active Members</option><option value="visitors">Visitors</option><option value="cell_group">Specific Cell Group</option><option value="zone">Specific Zone</option></select></div>
        <div class="mb-3"><label class="form-label">Subject (Email)</label><input v-model="form.subject" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Message *</label><textarea v-model="form.body" class="form-control" rows="5" placeholder="Use {{first_name}} for personalization"></textarea></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save Draft</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from "vue"
import dayjs from "dayjs"
import { communicationApi } from "@/api"
const fmt = d => dayjs(d).format("DD MMM YYYY HH:mm")
const tab = ref("broadcasts"); 
const broadcasts = ref([]); 
const logs = ref([])
const showModal = ref(false); 
const saving = ref(false)
const form = ref({ title:"", channels:["email"], target_group:"all_active", subject:"", body:"" })
async function load() { 
  if(tab.value==="broadcasts")
    {
      const{data}=await communicationApi.getBroadcasts();
      broadcasts.value=data.results||data
  } else {
    const{data}=await communicationApi.getLogs({page_size:50});
    logs.value=data.results||data
  } 
}
watch(tab, load)
function openBroadcastModal(){
  form.value={title:"",channels:["email"],target_group:"all_active",subject:"",body:""};
  showModal.value=true
}
async function save(){
  saving.value=true;
  try{
    await communicationApi.createBroadcast(form.value);
    showModal.value=false;load()
  }finally{
    saving.value=false
  }
}
async function send(id){
  if(!confirm("Send this broadcast now?"))
    return;
    await communicationApi.sendBroadcast(id);
    load()
}
async function retry(id){
  await communicationApi.retryLog(id);
  load()
}
onMounted(load)
</script>
<style scoped>
.btn-xs{
  padding:2px 7px;
  font-size:11px
}
</style>