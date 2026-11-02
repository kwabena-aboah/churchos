<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Facility Management</h1></div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" :class="tab==='bookings'?'active':''" @click="tab='bookings'">Room Bookings</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='maintenance'?'active':''" @click="tab='maintenance'">Maintenance</button>
        <button class="btn btn-primary btn-sm" @click="openModal"><i class="bi bi-plus me-1"></i>{{ tab==='bookings'?'Book Room':'Report Issue' }}</button>
      </div>
    </div>
    <div v-if="tab==='bookings'" class="cos-card p-0">
      <div class="table-responsive"><table class="cos-table">
        <thead><tr><th>Room</th><th>Title</th><th>Booked By</th><th>Start</th><th>End</th><th>Status</th><th></th></tr></thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td class="fw-semibold">{{ b.room_name }}</td>
            <td>{{ b.title }}</td>
            <td>{{ b.booked_by_name }}</td>
            <td class="text-muted small">{{ fmt(b.start_datetime) }}</td>
            <td class="text-muted small">{{ fmt(b.end_datetime) }}</td>
            <td><span class="status-badge" :class="b.status==='approved'?'badge-active':b.status==='rejected'?'badge-inactive':'badge-warning'">{{ b.status }}</span></td>
            <td><button v-if="b.status==='pending'" class="btn btn-xs btn-success" @click="approve(b.id)">Approve</button></td>
          </tr>
        </tbody>
      </table></div>
    </div>
    <div v-if="tab==='maintenance'" class="cos-card p-0">
      <div class="table-responsive"><table class="cos-table">
        <thead><tr><th>Room</th><th>Issue</th><th>Priority</th><th>Status</th><th>Reported</th></tr></thead>
        <tbody>
          <tr v-for="m in maintenance" :key="m.id">
            <td>{{ m.room_name || "General" }}</td>
            <td class="fw-semibold">{{ m.title }}</td>
            <td><span class="status-badge" :class="m.priority==='urgent'||m.priority==='high'?'badge-inactive':'badge-warning'">{{ m.priority }}</span></td>
            <td><span class="status-badge" :class="m.status==='completed'?'badge-active':m.status==='open'?'badge-inactive':'badge-warning'">{{ m.status }}</span></td>
            <td class="text-muted small">{{ fmt(m.created_at) }}</td>
          </tr>
        </tbody>
      </table></div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">{{ tab==='bookings'?'Book Room':'Report Maintenance Issue' }}</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body" v-if="tab==='bookings'">
        <div class="mb-3"><label class="form-label">Room *</label><select v-model="form.room" class="form-select"><option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option></select></div>
        <div class="mb-3"><label class="form-label">Title / Purpose *</label><input v-model="form.title" class="form-control" required /></div>
        <div class="row g-2"><div class="col-6"><label class="form-label">Start *</label><input v-model="form.start_datetime" type="datetime-local" class="form-control" required /></div><div class="col-6"><label class="form-label">End *</label><input v-model="form.end_datetime" type="datetime-local" class="form-control" required /></div></div>
      </div>
      <div class="modal-body" v-else>
        <div class="mb-3"><label class="form-label">Room</label><select v-model="maintForm.room" class="form-select"><option :value="null">General</option><option v-for="r in rooms" :key="r.id" :value="r.id">{{ r.name }}</option></select></div>
        <div class="mb-3"><label class="form-label">Issue Title *</label><input v-model="maintForm.title" class="form-control" required /></div>
        <div class="mb-3"><label class="form-label">Description *</label><textarea v-model="maintForm.description" class="form-control" rows="3" required></textarea></div>
        <div class="mb-3"><label class="form-label">Priority</label><select v-model="maintForm.priority" class="form-select"><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="urgent">Urgent</option></select></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving">Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from "vue"
import dayjs from "dayjs"
import { facilityApi } from "@/api"
const fmt = d => dayjs(d).format("DD MMM YYYY HH:mm")
const tab=ref("bookings"); const bookings=ref([]); const maintenance=ref([]); const rooms=ref([])
const showModal=ref(false); const saving=ref(false)
const form=ref({room:null,title:"",start_datetime:"",end_datetime:"",purpose:""}); const maintForm=ref({room:null,title:"",description:"",priority:"medium"})
async function load(){if(tab.value==="bookings"){const{data}=await facilityApi.getBookings();bookings.value=data.results||data}else{const{data}=await facilityApi.getMaintenance();maintenance.value=data.results||data}}
watch(tab,load)
function openModal(){form.value={room:null,title:"",start_datetime:"",end_datetime:"",purpose:""};maintForm.value={room:null,title:"",description:"",priority:"medium"};showModal.value=true}
async function approve(id){await facilityApi.approveBooking(id);load()}
async function save(){saving.value=true;try{tab.value==="bookings"?await facilityApi.createBooking(form.value):await facilityApi.createMaintenance(maintForm.value);showModal.value=false;load()}finally{saving.value=false}}
onMounted(async()=>{const{data}=await facilityApi.getRooms();rooms.value=data.results||data;load()})
</script>
<style scoped>.btn-xs{padding:2px 7px;font-size:11px}</style>