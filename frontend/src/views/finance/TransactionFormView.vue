<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Record Giving / Transaction</h1><p class="page-subtitle">Log a tithe, offering, donation, or expense</p></div>
      <RouterLink to="/finance" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Back</RouterLink>
    </div>
    <div class="row g-3">
      <div class="col-lg-8">
        <div class="cos-card">
          <form @submit.prevent="handleSubmit">
            <div class="form-section-title mt-0">Transaction Details</div>
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Transaction Type *</label>
                <select v-model="form.transaction_type" class="form-select" required @change="onTypeChange">
                  <option value="">Select type</option>
                  <option value="tithe">Tithe</option>
                  <option value="offering">Offering</option>
                  <option value="donation">Donation</option>
                  <option value="pledge_payment">Pledge Payment</option>
                  <option value="hall_rental">Hall Rental</option>
                  <option value="other_income">Other Income</option>
                  <option value="expense">Expense</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Category</label>
                <select v-model="form.category" class="form-select">
                  <option :value="null">None</option>
                  <option v-for="c in filteredCategories" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Amount ({{ settings.currency_code }}) *</label>
                <div class="input-group">
                  <span class="input-group-text">{{ settings.currency_symbol }}</span>
                  <input v-model="form.amount" type="number" step="0.01" min="0" class="form-control" required />
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label">Payment Method *</label>
                <select v-model="form.payment_method" class="form-select" required>
                  <option value="cash">Cash</option>
                  <option value="mobile_money">Mobile Money</option>
                  <option value="bank_transfer">Bank Transfer</option>
                  <option value="cheque">Cheque</option>
                  <option value="card">Card (POS)</option>
                  <option value="paystack">Paystack Online</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Transaction Date *</label>
                <input v-model="form.transaction_date" type="date" class="form-control" required />
              </div>
              <div class="col-md-6">
                <label class="form-label">Payment Reference</label>
                <input v-model="form.payment_reference" class="form-control" placeholder="MoMo ref, cheque no…" />
              </div>
              <div class="col-md-6" v-if="form.payment_method !== 'cash'">
                <label class="form-label">Bank Account</label>
                <select v-model="form.bank_account" class="form-select">
                  <option :value="null">None</option>
                  <option v-for="b in bankAccounts" :key="b.id" :value="b.id">{{ b.name }}</option>
                </select>
              </div>
              <div class="col-md-6" v-if="form.transaction_type === 'donation' || form.transaction_type === 'pledge_payment'">
                <label class="form-label">Cause / Project</label>
                <select v-model="form.cause" class="form-select">
                  <option :value="null">None</option>
                  <option v-for="c in causes" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label">Notes</label>
                <textarea v-model="form.notes" class="form-control" rows="2"></textarea>
              </div>
            </div>

            <div class="form-section-title">Member (optional — leave blank for anonymous)</div>
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label">Search Member</label>
                <div class="member-search-wrap">
                  <input v-model="memberSearch" type="text" class="form-control" placeholder="Type name or phone…" @input="searchMembers" />
                  <div class="member-dropdown" v-if="memberResults.length">
                    <div v-for="m in memberResults" :key="m.id" class="member-option" @click="selectMember(m)">
                      <strong>{{ m.full_name }}</strong> <span class="text-muted small ms-2">{{ m.member_number }} · {{ m.phone_primary }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="selectedMember" class="selected-member-chip mt-2">
                  <i class="bi bi-person-check-fill text-success me-2"></i>
                  {{ selectedMember.full_name }} ({{ selectedMember.member_number }})
                  <button type="button" class="btn-close btn-close-sm ms-auto" @click="clearMember"></button>
                </div>
              </div>
            </div>

            <div class="alert alert-danger mt-3" v-if="error">{{ error }}</div>
            <div class="d-flex gap-2 justify-content-end mt-4">
              <RouterLink to="/finance" class="btn btn-outline-secondary">Cancel</RouterLink>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ saving ? 'Saving…' : 'Record Transaction' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="cos-card">
          <h6 class="fw-bold mb-3">Tips</h6>
          <div class="tip" v-for="t in tips[form.transaction_type] || tips.default" :key="t">
            <i class="bi bi-info-circle text-primary me-2"></i>{{ t }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { financeApi, membersApi } from '@/api'
import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const settingsStore = useSettingsStore()
const settings = settingsStore.settings

const form = ref({
  transaction_type: 'tithe', category: null, amount: '', payment_method: 'cash',
  transaction_date: dayjs().format('YYYY-MM-DD'), payment_reference: '',
  bank_account: null, cause: null, pledge: null, notes: '', member: null,
})
const categories = ref([])
const bankAccounts = ref([])
const causes = ref([])
const memberSearch = ref('')
const memberResults = ref([])
const selectedMember = ref(null)
const saving = ref(false)
const error = ref('')

const filteredCategories = computed(() => categories.value.filter(c => !c.transaction_type || c.transaction_type === form.value.transaction_type))

const tips = {
  tithe: ['Tithes are 10% of income', 'Always link a tithe to a member for proper tracking'],
  offering: ['Offerings are collected during services', 'Associate with the service type if applicable'],
  expense: ['Expenses above the threshold require approval', 'Attach a receipt photo if available'],
  default: ['All transactions generate a receipt automatically', 'Verified transactions require a secondary approval'],
}

let memberTimer
async function searchMembers() {
  if (memberSearch.value.length < 2) { memberResults.value = []; return }
  clearTimeout(memberTimer)
  memberTimer = setTimeout(async () => {
    const { data } = await membersApi.list({ search: memberSearch.value, page_size: 8 })
    memberResults.value = data.results || data
  }, 300)
}

function selectMember(m) { selectedMember.value = m; form.value.member = m.id; memberSearch.value = ''; memberResults.value = [] }
function clearMember() { selectedMember.value = null; form.value.member = null }
function onTypeChange() { form.value.category = null; form.value.cause = null }

async function handleSubmit() {
  error.value = ''; saving.value = true
  try {
    await financeApi.createTransaction({ ...form.value })
    router.push('/finance')
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Error saving transaction.')
  } finally { saving.value = false }
}

onMounted(async () => {
  const [cats, banks, causesRes] = await Promise.all([financeApi.getCategories(), financeApi.getBankAccounts(), financeApi.getCauses()])
  categories.value = cats.data.results || cats.data
  bankAccounts.value = banks.data.results || banks.data
  causes.value = causesRes.data.results || causesRes.data
})
</script>

<style scoped>
.member-search-wrap { position: relative }
.member-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: #fff; border: 1px solid var(--cos-border); border-radius: 8px; z-index: 100; max-height: 200px; overflow-y: auto; box-shadow: var(--cos-shadow-lg) }
.member-option { padding: 9px 14px; cursor: pointer; font-size: 13px }
.member-option:hover { background: var(--cos-primary-light) }
.selected-member-chip { display: flex; align-items: center; background: var(--cos-primary-light); border-radius: 8px; padding: 8px 12px; font-size: 13px; font-weight: 600; color: var(--cos-primary) }
.tip { font-size: 12.5px; margin-bottom: 10px; color: var(--cos-text-muted); line-height: 1.6 }
</style>
