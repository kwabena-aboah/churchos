<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Inventory</h1><p class="page-subtitle">{{ pagination.count }} items tracked</p></div><button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>Add Item</button></div>
    <div class="row g-3 mb-3" v-if="summary">
      <div class="col-md-3"><div class="stat-card"><div class="stat-icon" style="background:#e8f5ee"><i class="bi bi-box-seam" style="color:#1a6b3c"></i></div><div><div class="stat-value">{{ summary.total_items }}</div><div class="stat-label">Total Items</div></div></div></div>
      <div class="col-md-3"><div class="stat-card"><div class="stat-icon" style="background:#fff3cd"><i class="bi bi-currency-dollar" style="color:#856404"></i></div><div><div class="stat-value">{{ fmtCur(summary.total_value) }}</div><div class="stat-label">Total Value</div></div></div></div>
    </div>
    <div class="cos-card mb-3"><div class="row g-2">
      <div class="col-md-4"><input v-model="search" class="form-control form-control-sm" placeholder="Search items…" @input="debouncedLoad" /></div>
      <div class="col-md-3"><select v-model="conditionFilter" class="form-select form-select-sm" @change="load"><option value="">All Conditions</option><option value="new">New</option><option value="good">Good</option><option value="fair">Fair</option><option value="poor">Poor</option></select></div>
    </div></div>
    <div class="cos-card p-0">
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Item</th><th>Category</th><th>Location</th><th>Condition</th><th>Qty</th><th>Value</th><th></th></tr></thead>
          <tbody>
            <tr v-for="i in items" :key="i.id">
              <td><div class="fw-semibold">{{ i.name }}</div><div class="text-muted" style="font-size:11px">{{ i.serial_number || "" }}</div></td>
              <td>{{ i.category_name || "—" }}</td>
              <td>{{ i.location || "—" }}</td>
              <td><span class="status-badge" :class="condClass(i.condition)">{{ i.condition }}</span></td>
              <td>{{ i.quantity }}</td>
              <td>{{ i.current_value ? fmtCur(i.current_value) : "—" }}</td>
              <td><button class="btn btn-xs btn-outline-primary" @click="openModal(i)"><i class="bi bi-pencil"></i></button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog modal-lg"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">{{ editing?"Edit Item":"Add Item" }}</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body"><div class="row g-3">
        <div class="col-md-6"><label class="form-label">Item Name *</label><input v-model="form.name" class="form-control" required /></div>
        <div class="col-md-6"><label class="form-label">Category</label><select v-model="form.category" class="form-select"><option :value="null">None</option><option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option></select></div>
        <div class="col-md-4"><label class="form-label">Serial Number</label><input v-model="form.serial_number" class="form-control" /></div>
        <div class="col-md-4"><label class="form-label">Location</label><input v-model="form.location" class="form-control" /></div>
        <div class="col-md-4"><label class="form-label">Department</label><input v-model="form.department" class="form-control" /></div>
        <div class="col-md-3"><label class="form-label">Condition</label><select v-model="form.condition" class="form-select"><option value="new">New</option><option value="good">Good</option><option value="fair">Fair</option><option value="poor">Poor</option></select></div>
        <div class="col-md-3"><label class="form-label">Quantity</label><input v-model="form.quantity" type="number" class="form-control" /></div>
        <div class="col-md-3"><label class="form-label">Purchase Price</label><input v-model="form.purchase_price" type="number" step="0.01" class="form-control" /></div>
        <div class="col-md-3"><label class="form-label">Current Value</label><input v-model="form.current_value" type="number" step="0.01" class="form-control" /></div>
        <div class="col-md-4"><label class="form-label">Purchase Date</label><input v-model="form.purchase_date" type="date" class="form-control" /></div>
        <div class="col-md-4"><label class="form-label">Useful Life (yrs)</label><input v-model="form.useful_life_years" type="number" class="form-control" /></div>
      </div></div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { inventoryApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const condClass = c => ({new:"badge-active",good:"badge-visitor",fair:"badge-warning",poor:"badge-inactive",written_off:"badge-inactive"}[c]||"badge-visitor")
const items=ref([]); const categories=ref([]); const summary=ref(null); const loading=ref(false)
const search=ref(""); const conditionFilter=ref(""); const pagination=ref({count:0})
const showModal=ref(false); const editing=ref(null); const saving=ref(false)
const form=ref({name:"",category:null,serial_number:"",location:"",department:"",condition:"good",quantity:1,purchase_price:"",current_value:"",purchase_date:"",useful_life_years:""})
let dt; function debouncedLoad(){clearTimeout(dt);dt=setTimeout(load,400)}
async function load(){loading.value=true;const p={};if(search.value)p.search=search.value;if(conditionFilter.value)p.condition=conditionFilter.value;const{data}=await inventoryApi.list(p);items.value=data.results||data;pagination.value.count=data.count||items.value.length;loading.value=false}
function openModal(i=null){editing.value=i;form.value=i?{...i}:{name:"",category:null,serial_number:"",location:"",department:"",condition:"good",quantity:1,purchase_price:"",current_value:"",purchase_date:"",useful_life_years:""};showModal.value=true}
async function save(){saving.value=true;try{editing.value?await inventoryApi.update(editing.value.id,form.value):await inventoryApi.create(form.value);showModal.value=false;load()}finally{saving.value=false}}
onMounted(async()=>{const[s,c]=await Promise.all([inventoryApi.summary(),inventoryApi.getCategories()]);summary.value=s.data;categories.value=c.data.results||c.data;load()})
</script>
<style scoped>.btn-xs{padding:2px 7px;font-size:11px}</style>