<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Prayer Requests</h1></div><button class="btn btn-primary btn-sm" @click="openModal"><i class="bi bi-plus me-1"></i>New Request</button></div>
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="p in prayers" :key="p.id">
        <div class="cos-card">
          <div class="d-flex justify-content-between mb-2">
            <span class="status-badge" :class="p.status==='answered'?'badge-active':p.status==='praying'?'badge-visitor':'badge-warning'">{{ p.status }}</span>
            <span class="badge bg-light text-dark border">{{ p.privacy }}</span>
          </div>
          <h6 class="fw-bold mb-1">{{ p.title }}</h6>
          <p class="text-muted small mb-3">{{ p.request_text.slice(0,120) }}{{ p.request_text.length>120?"…":"" }}</p>
          <div class="text-muted small mb-3">{{ p.member_name || p.submitter_name }}</div>
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-primary flex-grow-1" @click="pray(p.id)"><i class="bi bi-hand-thumbs-up me-1"></i>Pray ({{ p.prayer_count }})</button>
            <button class="btn btn-sm btn-success" @click="markAnswered(p)" v-if="p.status!=='answered'">Answered</button>
          </div>
        </div>
      </div>
      <div class="col-12" v-if="prayers.length===0"><div class="cos-card cos-empty"><i class="bi bi-hand-thumbs-up"></i><p>No prayer requests.</p></div></div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">New Prayer Request</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body">
        <div class="mb-3"><label class="form-label">Title *</label><input v-model="form.title" class="form-control" required /></div>
        <div class="mb-3"><label class="form-label">Request *</label><textarea v-model="form.request_text" class="form-control" rows="4" required></textarea></div>
        <div class="mb-3"><label class="form-label">Privacy</label><select v-model="form.privacy" class="form-select"><option value="public">Public</option><option value="leaders_only">Leaders Only</option><option value="private">Private</option></select></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving">Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { prayerApi } from "@/api"
const prayers=ref([]); const showModal=ref(false); const saving=ref(false)
const form=ref({title:"",request_text:"",privacy:"leaders_only"})
async function load(){const{data}=await prayerApi.list();prayers.value=data.results||data}
function openModal(){form.value={title:"",request_text:"",privacy:"leaders_only"};showModal.value=true}
async function save(){saving.value=true;try{await prayerApi.create(form.value);showModal.value=false;load()}finally{saving.value=false}}
async function pray(id){await prayerApi.pray(id);load()}
async function markAnswered(p){const t=prompt("Testimony (optional):");await prayerApi.markAnswered(p.id,t||"");load()}
onMounted(load)
</script>