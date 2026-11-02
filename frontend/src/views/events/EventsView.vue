<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Events</h1><p class="page-subtitle">{{ events.length }} events</p></div><button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>New Event</button></div>
    <div class="cos-card mb-3">
      <div class="row g-2">
        <div class="col-md-4"><input v-model="search" type="text" class="form-control form-control-sm" placeholder="Search events…" @input="debouncedLoad" /></div>
        <div class="col-md-3"><select v-model="typeFilter" class="form-select form-select-sm" @change="loadEvents"><option value="">All Types</option><option value="service">Service</option><option value="conference">Conference</option><option value="outreach">Outreach</option><option value="meeting">Meeting</option><option value="training">Training</option></select></div>
      </div>
    </div>
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="e in events" :key="e.id">
        <div class="cos-card event-card">
          <div class="event-type-tag">{{ e.event_type }}</div>
          <h6 class="fw-bold mt-2 mb-1">{{ e.title }}</h6>
          <div class="text-muted small mb-2"><i class="bi bi-calendar3 me-1"></i>{{ fmt(e.start_datetime) }}</div>
          <div class="text-muted small mb-2" v-if="e.venue_name"><i class="bi bi-geo-alt me-1"></i>{{ e.venue_name }}</div>
          <div class="d-flex align-items-center justify-content-between mt-3">
            <div class="small"><span :class="e.is_paid ? 'text-warning' : 'text-success'"><i :class="`bi ${e.is_paid ? 'bi-ticket-perforated' : 'bi-gift'} me-1`"></i>{{ e.is_paid ? fmtCur(e.ticket_price) : 'Free' }}</span></div>
            <RouterLink 
              :to="`/events/${e.id}`" 
              class="btn btn-sm btn-outline-primary"
            >
              Details
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog modal-lg"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">{{ editing ? "Edit Event" : "New Event" }}</h5><button class="btn-close" @click="showModal=false"></button></div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-12"><label class="form-label">Title *</label><input v-model="form.title" class="form-control" required /></div>
            <div class="col-md-4"><label class="form-label">Type</label><select v-model="form.event_type" class="form-select"><option value="service">Service</option><option value="conference">Conference</option><option value="outreach">Outreach</option><option value="meeting">Meeting</option><option value="concert">Concert/Program</option><option value="training">Training</option></select></div>
            <div class="col-md-4"><label class="form-label">Start *</label><input v-model="form.start_datetime" type="datetime-local" class="form-control" required /></div>
            <div class="col-md-4"><label class="form-label">End</label><input v-model="form.end_datetime" type="datetime-local" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Venue</label><input v-model="form.venue_name" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Capacity</label><input v-model="form.capacity" type="number" class="form-control" /></div>
            <div class="col-12"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
            <div class="col-md-4"><div class="form-check mt-4"><input class="form-check-input" type="checkbox" v-model="form.requires_registration" id="reg" /><label class="form-check-label" for="reg">Requires Registration</label></div></div>
            <div class="col-md-4"><div class="form-check mt-4"><input class="form-check-input" type="checkbox" v-model="form.is_paid" id="paid" /><label class="form-check-label" for="paid">Paid Event</label></div></div>
            <div class="col-md-4" v-if="form.is_paid"><label class="form-label">Ticket Price</label><input v-model="form.ticket_price" type="number" step="0.01" class="form-control" /></div>
          </div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="saveEvent" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
      </div></div>
    </div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { eventsApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const fmt = d => dayjs(d).format("DD MMM YYYY, h:mm A")
const events = ref([]); const search = ref(""); const typeFilter = ref(""); const showModal = ref(false); const editing = ref(null); const saving = ref(false)
const form = ref({ title:"", event_type:"service", start_datetime:"", end_datetime:"", venue_name:"", capacity:null, description:"", requires_registration:false, is_paid:false, ticket_price:0 })
let dt; function debouncedLoad() { clearTimeout(dt); dt=setTimeout(loadEvents, 400) }
async function loadEvents() { const p={}; if(search.value) p.search=search.value; if(typeFilter.value) p.event_type=typeFilter.value; const { data }=await eventsApi.list(p); events.value=data.results||data }
function openModal(e=null) { editing.value=e; form.value=e?{...e}:{title:"",event_type:"service",start_datetime:"",end_datetime:"",venue_name:"",capacity:null,description:"",requires_registration:false,is_paid:false,ticket_price:0}; showModal.value=true }
async function saveEvent() { saving.value=true; try { editing.value?await eventsApi.update(editing.value.id,form.value):await eventsApi.create(form.value); showModal.value=false; loadEvents() } finally { saving.value=false } }
onMounted(loadEvents)
</script>
<style scoped>.event-card { position:relative }.event-type-tag { display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:.08em; background:var(--cos-primary-light); color:var(--cos-primary); padding:2px 8px; border-radius:4px; font-weight:700 }</style>