<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Budget</h1><p class="page-subtitle">Annual budgets and variance tracking</p></div><button class="btn btn-primary btn-sm" @click="openModal"><i class="bi bi-plus me-1"></i>New Budget Year</button></div>
    <div class="row g-3 mb-3">
      <div class="col-md-3" v-for="y in years" :key="y.id">
        <div class="cos-card cursor-pointer" :class="selectedYear?.id===y.id?'border-primary':''" @click="selectYear(y)" style="cursor:pointer">
          <div class="d-flex justify-content-between"><span class="fw-bold fs-5">{{ y.year }}</span><span class="status-badge" :class="y.is_approved?'badge-active':'badge-warning'">{{ y.is_approved?"Approved":"Draft" }}</span></div>
          <div class="text-success small mt-1">Income: {{ fmtCur(y.total_income_budget) }}</div>
          <div class="text-danger small">Expense: {{ fmtCur(y.total_expense_budget) }}</div>
        </div>
      </div>
    </div>
    <div v-if="selectedYear" class="cos-card">
      <div class="d-flex justify-content-between mb-3">
        <h6 class="fw-bold mb-0">Budget Lines — {{ selectedYear.year }}</h6>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-success" @click="approveBudget" v-if="!selectedYear.is_approved">Approve Budget</button>
          <button class="btn btn-sm btn-primary" @click="openLineModal">+ Add Line</button>
        </div>
      </div>
      <div class="table-responsive">
        <table class="cos-table">
          <thead><tr><th>Category</th><th>Department</th><th>Type</th><th>Budgeted</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th></tr></thead>
          <tbody>
            <tr v-for="l in lines" :key="l.id">
              <td class="fw-semibold">{{ l.category_name }}</td>
              <td class="text-muted">{{ l.department || "—" }}</td>
              <td><span class="status-badge" :class="l.line_type==='income'?'badge-active':'badge-inactive'">{{ l.line_type }}</span></td>
              <td class="fw-bold">{{ fmtCur(l.amount) }}</td>
              <td>{{ fmtCur(l.q1_amount) }}</td>
              <td>{{ fmtCur(l.q2_amount) }}</td>
              <td>{{ fmtCur(l.q3_amount) }}</td>
              <td>{{ fmtCur(l.q4_amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">{{ lineModal?"Add Budget Line":"New Budget Year" }}</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body" v-if="!lineModal">
        <div class="mb-3"><label class="form-label">Year *</label><input v-model="yearForm.year" type="number" class="form-control" /></div>
        <div class="mb-3"><label class="form-label">Title</label><input v-model="yearForm.title" class="form-control" /></div>
        <div class="row g-2"><div class="col-6"><label class="form-label">Start Date</label><input v-model="yearForm.start_date" type="date" class="form-control" /></div><div class="col-6"><label class="form-label">End Date</label><input v-model="yearForm.end_date" type="date" class="form-control" /></div></div>
      </div>
      <div class="modal-body" v-else>
        <div class="mb-3"><label class="form-label">Category</label><select v-model="lineForm.category" class="form-select"><option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option></select></div>
        <div class="mb-3"><label class="form-label">Type</label><select v-model="lineForm.line_type" class="form-select"><option value="income">Income</option><option value="expense">Expense</option></select></div>
        <div class="mb-3"><label class="form-label">Total Amount</label><input v-model="lineForm.amount" type="number" step="0.01" class="form-control" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { budgetApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const years = ref([]); const selectedYear = ref(null); const lines = ref([]); const categories = ref([])
const showModal = ref(false); const lineModal = ref(false); const saving = ref(false)
const yearForm = ref({ year: dayjs().year()+1, title: "", start_date: "", end_date: "" })
const lineForm = ref({ category: null, line_type: "expense", amount: 0 })
async function loadYears() { const { data } = await budgetApi.getYears(); years.value = data.results || data }
async function selectYear(y) { selectedYear.value = y; const { data } = await budgetApi.getLines({ budget_year: y.id }); lines.value = data.results || data }
function openModal() { lineModal.value = false; showModal.value = true }
function openLineModal() { lineModal.value = true; showModal.value = true }
async function approveBudget() { await budgetApi.approveYear(selectedYear.value.id); loadYears() }
async function save() { saving.value = true; try { if (lineModal.value) { await budgetApi.createLine({ ...lineForm.value, budget_year: selectedYear.value.id }); selectYear(selectedYear.value) } else { await budgetApi.createYear(yearForm.value); loadYears() }; showModal.value = false } finally { saving.value = false } }
onMounted(async () => { const { data } = await budgetApi.getCategories(); categories.value = data.results || data; loadYears() })
</script>