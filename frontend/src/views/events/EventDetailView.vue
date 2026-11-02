<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">{{ event?.title }}</h1><p class="page-subtitle">{{ event?.event_type }} · {{ fmt(event?.start_datetime) }}</p></div><RouterLink to="/events" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Back</RouterLink></div>
    <div v-if="!event" class="cos-spinner"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-3">
      <div class="col-lg-8">
        <div class="cos-card mb-3">
          <div class="row g-3 text-center">
            <div class="col-3"><div class="text-muted small">Registered</div><div class="fw-bold fs-4">{{ event.registered_count }}</div></div>
            <div class="col-3"><div class="text-muted small">Capacity</div><div class="fw-bold fs-4">{{ event.capacity || "∞" }}</div></div>
            <div class="col-3"><div class="text-muted small">Venue</div><div class="fw-bold small">{{ event.venue_name || "TBD" }}</div></div>
            <div class="col-3"><div class="text-muted small">Ticket</div><div class="fw-bold">{{ event.is_paid ? fmtCur(event.ticket_price) : "Free" }}</div></div>
          </div>
        </div>
        <div class="cos-card mb-3">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0">Registrations ({{ registrations.length }})</h6>
            <div class="d-flex gap-2">
              <input v-model="ticketScan" type="text" class="form-control form-control-sm" placeholder="Scan/enter ticket ref…" @keyup.enter="checkIn" style="width:200px" />
              <button class="btn btn-sm btn-success" @click="checkIn">Check In</button>
            </div>
          </div>
          <div class="table-responsive">
            <table class="cos-table">
              <thead><tr><th>Name</th><th>Ticket</th><th>Status</th><th>Checked In</th></tr></thead>
              <tbody>
                <tr v-for="r in registrations" :key="r.id">
                  <td>{{ r.member_name }}</td>
                  <td><code>{{ r.ticket_ref }}</code></td>
                  <td><span class="status-badge badge-active">{{ r.status }}</span></td>
                  <td><i :class="`bi ${r.checked_in ? 'bi-check-circle-fill text-success' : 'bi-circle text-muted'}`"></i> {{ r.checked_in ? fmt(r.checked_in_at) : "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="cos-card mb-3">
          <h6 class="fw-bold mb-3">Register Attendee</h6>
          <div class="mb-2"><input v-model="regSearch" type="text" class="form-control form-control-sm" placeholder="Search member…" @input="searchMembers" /></div>
          <div class="member-dropdown" v-if="memberResults.length"><div v-for="m in memberResults" :key="m.id" class="member-option" @click="registerMember(m)">{{ m.full_name }}</div></div>
          <div class="text-muted small mt-2">Or register a guest:</div>
          <div class="row g-2 mt-1"><div class="col-7"><input v-model="guestName" type="text" class="form-control form-control-sm" placeholder="Guest name" /></div><div class="col-5"><button class="btn btn-sm btn-outline-primary w-100" @click="registerGuest">Register</button></div></div>
        </div>
        <div class="cos-card">
          <h6 class="fw-bold mb-2">Event Info</h6>
          <div class="info-row"><i class="bi bi-calendar3"></i><span>{{ fmt(event.start_datetime) }}</span></div>
          <div class="info-row" v-if="event.venue_name"><i class="bi bi-geo-alt"></i><span>{{ event.venue_name }}</span></div>
          <div class="info-row" v-if="event.description"><i class="bi bi-info-circle"></i><span>{{ event.description }}</span></div>
          <div class="info-row" v-if="event.online_link"><i class="bi bi-camera-video"></i><a :href="event.online_link" target="_blank">Join Online</a></div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import dayjs from "dayjs"
import { eventsApi, membersApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const route = useRoute()
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const fmt = d => d ? dayjs(d).format("DD MMM YYYY, h:mm A") : "—"
const event = ref(null); const registrations = ref([]); const ticketScan = ref(""); const regSearch = ref(""); const memberResults = ref([]); const guestName = ref("")
async function load() { const { data } = await eventsApi.get(route.params.id); event.value = data; const r = await eventsApi.getRegistrations({ event: route.params.id }); registrations.value = r.data.results || r.data }
async function checkIn() { if (!ticketScan.value) return; try { const { data } = await eventsApi.checkinByTicket(ticketScan.value.trim()); alert(`✅ Checked in: ${data.name}`); ticketScan.value = ""; load() } catch { alert("Invalid ticket.") } }
let t; async function searchMembers() { clearTimeout(t); t = setTimeout(async () => { if (regSearch.value.length < 2) { memberResults.value = []; return } const { data } = await membersApi.list({ search: regSearch.value, page_size: 8 }); memberResults.value = data.results || data }, 300) }
async function registerMember(m) { await eventsApi.register({ event: route.params.id, member: m.id }); regSearch.value = ""; memberResults.value = []; load() }
async function registerGuest() { if (!guestName.value) return; await eventsApi.register({ event: route.params.id, guest_name: guestName.value }); guestName.value = ""; load() }
onMounted(load)
</script>
<style scoped>.info-row { display:flex; gap:10px; align-items:flex-start; padding:6px 0; border-bottom:1px solid var(--cos-border); font-size:13px } .info-row i { color:var(--cos-primary); width:18px; flex-shrink:0; margin-top:2px } .member-dropdown { background:#fff; border:1px solid var(--cos-border); border-radius:8px; max-height:160px; overflow-y:auto } .member-option { padding:8px 12px; cursor:pointer; font-size:13px } .member-option:hover { background:var(--cos-primary-light) }</style>