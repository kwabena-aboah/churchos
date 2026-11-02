<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Procurement</h1></div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" :class="tab==='requests'?'active':''" @click="tab='requests'">Requests</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='orders'?'active':''" @click="tab='orders'">Purchase Orders</button>
        <button class="btn btn-outline-primary btn-sm" :class="tab==='vendors'?'active':''" @click="tab='vendors'">Vendors</button>
        <button class="btn btn-primary btn-sm" @click="openModal"><i class="bi bi-plus me-1"></i>New Request</button>
      </div>
    </div>
    <div class="cos-card p-0">
      <div class="table-responsive" v-if="tab==='requests'">
        <table class="cos-table">
          <thead><tr><th>Reference</th><th>Title</th><th>Department</th><th>Est. Total</th><th>Status</th><th>Date</th><th></th></tr></thead>
          <tbody>
            <tr v-for="r in requests" :key="r.id">
              <td><code class="text-primary">{{ r.reference }}</code></td>
              <td class="fw-semibold">{{ r.title }}</td>
              <td>{{ r.department || "—" }}</td>
              <td>{{ fmtCur(r.total_estimated) }}</td>
              <td><span class="status-badge" :class="statusClass(r.status)">{{ r.status }}</span></td>
              <td class="text-muted small">{{ fmt(r.created_at) }}</td>
              <td>
                <button v-if="r.status==='pending'" class="btn btn-xs btn-success me-1" @click="approve(r.id)" title="Approve"><i class="bi bi-check2"></i></button>
                <button v-if="r.status==='pending'" class="btn btn-xs btn-danger" @click="reject(r.id)" title="Reject"><i class="bi bi-x"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-responsive" v-if="tab==='orders'">
        <table class="cos-table">
          <thead>
            <tr>
              <th>PO Ref</th>
              <th>Vendor</th>
              <th>Total</th>
              <th>Status</th>
              <th>Order Date</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in orders" :key="o.id">
              <td><code class="text-primary">{{ o.reference }}</code></td>
              <td>{{ o.vendor_name }}</td>
              <td class="fw-bold">{{ fmtCur(o.total_amount) }}</td>
              <td><span class="status-badge" :class="statusClass(o.status)">{{ o.status }}</span></td>
              <td>{{ fmt(o.order_date) }}</td>
              <td><button v-if="o.status!=='received'" class="btn btn-xs btn-success" @click="markReceived(o.id)">Mark Received</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-responsive" v-if="tab==='vendors'">
        <table class="cos-table">
          <thead>
            <tr>
              <th>Vendor</th>
              <th>Contact</th>
              <th>Phone</th>
              <th>Category</th>
              <th>Rating</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in vendors" :key="v.id">
              <td class="fw-semibold">{{ v.name }}</td>
              <td>{{ v.contact_person || "—" }}</td>
              <td>{{ v.phone || "—" }}</td>
              <td>{{ v.category || "—" }}</td>
              <td>{{ "⭐".repeat(v.rating) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">New Purchase Request</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body">
        <div class="mb-3"><label class="form-label">Title *</label><input v-model="form.title" class="form-control" required /></div>
        <div class="mb-3"><label class="form-label">Department</label><input v-model="form.department" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Estimated Total</label><input v-model="form.total_estimated" type="number" step="0.01" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Date Needed</label><input v-model="form.date_needed" type="date" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Justification *</label><textarea v-model="form.justification" class="form-control" rows="3" required></textarea></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Submit</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from "vue"
import dayjs from "dayjs"
import { procurementApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const fmt = d => dayjs(d).format("DD MMM YYYY")
const statusClass = s => ({pending:"badge-warning",approved:"badge-active",rejected:"badge-inactive",ordered:"badge-visitor",received:"badge-active",cancelled:"badge-inactive",draft:"badge-warning"}[s]||"badge-visitor")
const tab = ref("requests"); const requests = ref([]); const orders = ref([]); const vendors = ref([])
const showModal = ref(false); const saving = ref(false)
const form = ref({ title:"", department:"", total_estimated:0, date_needed:"", justification:"" })
async function load() { if(tab.value==="requests"){const{data}=await procurementApi.getRequests();requests.value=data.results||data} else if(tab.value==="orders"){const{data}=await procurementApi.getOrders();orders.value=data.results||data} else {const{data}=await procurementApi.getVendors();vendors.value=data.results||data} }
watch(tab, load)
function openModal(){form.value={title:"",department:"",total_estimated:0,date_needed:"",justification:""};showModal.value=true}
async function approve(id){await procurementApi.approveRequest(id);load()}
async function reject(id){const r=prompt("Rejection reason:");await procurementApi.rejectRequest(id,r);load()}
async function markReceived(id){await procurementApi.markReceived(id);load()}
async function save(){saving.value=true;try{await procurementApi.createRequest(form.value);showModal.value=false;load()}finally{saving.value=false}}
onMounted(load)
</script>
<style scoped>.btn-xs{padding:2px 7px;font-size:11px}</style>