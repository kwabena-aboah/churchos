<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">System Settings</h1><p class="page-subtitle">Configure your church management system</p></div><button class="btn btn-primary btn-sm" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save Changes</button></div>
    <div class="row g-3">
      <div class="col-lg-3">
        <div class="cos-card p-2">
          <div v-for="tab in tabs" :key="tab.id" class="settings-tab" :class="activeTab===tab.id?'active':''" @click="activeTab=tab.id">
            <i :class="`bi ${tab.icon} me-2`"></i>{{ tab.label }}
          </div>
        </div>
      </div>
      <div class="col-lg-9">
        <div class="cos-card">
          <div v-if="activeTab==='church'">
            <div class="form-section-title mt-0">Church Profile</div>
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">Church Name *</label><input v-model="form.church_name" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Tagline</label><input v-model="form.church_tagline" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Denomination</label><input v-model="form.church_denomination" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Founded Year</label><input v-model="form.founded_year" type="number" class="form-control" /></div>
              <div class="col-12"><label class="form-label">Address</label><textarea v-model="form.address" class="form-control" rows="2"></textarea></div>
              <div class="col-md-4"><label class="form-label">City</label><input v-model="form.city" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Country</label><input v-model="form.country" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" type="email" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Website</label><input v-model="form.website" type="url" class="form-control" /></div>
            </div>
          </div>
          <div v-if="activeTab==='branding'">
            <div class="form-section-title mt-0">Branding & Colors</div>
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">Logo</label><input type="file" class="form-control" @change="e=>logoFile=e.target.files[0]" accept="image/*" /><img v-if="form.logo_url" :src="form.logo_url" class="mt-2 rounded" style="height:60px" /></div>
              <div class="col-md-6"><label class="form-label">Favicon</label><input type="file" class="form-control" @change="e=>faviconFile=e.target.files[0]" accept="image/*" /></div>
              <div class="col-md-4"><label class="form-label">Primary Color</label><div class="d-flex gap-2"><input v-model="form.primary_color" type="color" class="form-control form-control-color" /><input v-model="form.primary_color" type="text" class="form-control" /></div></div>
              <div class="col-md-4"><label class="form-label">Secondary Color</label><div class="d-flex gap-2"><input v-model="form.secondary_color" type="color" class="form-control form-control-color" /><input v-model="form.secondary_color" type="text" class="form-control" /></div></div>
              <div class="col-md-4"><label class="form-label">Accent Color</label><div class="d-flex gap-2"><input v-model="form.accent_color" type="color" class="form-control form-control-color" /><input v-model="form.accent_color" type="text" class="form-control" /></div></div>
            </div>
          </div>
          <div v-if="activeTab==='finance'">
            <div class="form-section-title mt-0">Finance & Locale</div>
            <div class="row g-3">
              <div class="col-md-4"><label class="form-label">Currency Code</label><input v-model="form.currency_code" class="form-control" placeholder="GHS" /></div>
              <div class="col-md-4"><label class="form-label">Currency Symbol</label><input v-model="form.currency_symbol" class="form-control" placeholder="₵" /></div>
              <div class="col-md-4"><label class="form-label">Financial Year Start Month</label><select v-model="form.financial_year_start_month" class="form-select"><option v-for="i in 12" :key="i" :value="i">{{ monthName(i) }}</option></select></div>
              <div class="col-md-6"><label class="form-label">Approval Threshold 1 (single)</label><input v-model="form.procurement_approval_threshold_1" type="number" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Approval Threshold 2 (double)</label><input v-model="form.procurement_approval_threshold_2" type="number" class="form-control" /></div>
            </div>
          </div>
          <div v-if="activeTab==='notifications'">
            <div class="form-section-title mt-0">Notification Toggles</div>
            <div class="row g-3">
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_birthday_email" /><label class="form-check-label">Birthday Email</label></div></div>
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_birthday_sms" /><label class="form-check-label">Birthday SMS</label></div></div>
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_birthday_whatsapp" /><label class="form-check-label">Birthday WhatsApp</label></div></div>
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_payment_receipt_email" /><label class="form-check-label">Receipt Email</label></div></div>
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_event_reminders" /><label class="form-check-label">Event Reminders</label></div></div>
              <div class="col-md-4"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.ai_weekly_briefing" /><label class="form-check-label">AI Weekly Briefing</label></div></div>
              <div class="col-12" v-if="form.ai_weekly_briefing"><label class="form-label">Briefing Recipients (comma-separated emails)</label><input v-model="form.ai_briefing_recipients" class="form-control" /></div>
            </div>
          </div>
          <div v-if="activeTab==='integrations'">
            <div class="form-section-title mt-0">Paystack</div>
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">Public Key</label><input v-model="form.paystack_public_key" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Secret Key</label><input v-model="form.paystack_secret_key" type="password" class="form-control" /></div>
            </div>
            <div class="form-section-title">Twilio (SMS)</div>
            <div class="row g-3">
              <div class="col-md-4"><label class="form-label">Account SID</label><input v-model="form.twilio_account_sid" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Auth Token</label><input v-model="form.twilio_auth_token" type="password" class="form-control" /></div>
              <div class="col-md-4"><label class="form-label">Sender ID</label><input v-model="form.twilio_sender_id" class="form-control" /></div>
            </div>
            <div class="form-section-title">WhatsApp (Meta Cloud API)</div>
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">API Token</label><input v-model="form.whatsapp_api_token" type="password" class="form-control" /></div>
              <div class="col-md-6"><label class="form-label">Phone Number ID</label><input v-model="form.whatsapp_phone_id" class="form-control" /></div>
            </div>
            <div class="form-section-title">AI Features</div>
            <div class="row g-3">
              <div class="col-md-6"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" v-model="form.enable_ai_features" /><label class="form-check-label">Enable AI Features</label></div></div>
            </div>
          </div>
          <div class="alert alert-success mt-3" v-if="saved"><i class="bi bi-check-circle me-2"></i>Settings saved successfully.</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { settingsApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const settingsStore = useSettingsStore()
const monthName = m => dayjs().month(m-1).format("MMMM")
const activeTab = ref("church"); const saving = ref(false); const saved = ref(false)
const logoFile = ref(null); const faviconFile = ref(null)
const form = ref({})
const tabs = [
  { id:"church", icon:"bi-building", label:"Church Profile" },
  { id:"branding", icon:"bi-palette", label:"Branding" },
  { id:"finance", icon:"bi-currency-dollar", label:"Finance & Locale" },
  { id:"notifications", icon:"bi-bell", label:"Notifications" },
  { id:"integrations", icon:"bi-plug", label:"Integrations & AI" },
]
async function load() { const { data } = await settingsApi.get(); form.value = data }
async function save() {
  saving.value = true; saved.value = false
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([k,v]) => { if(v!==null&&v!==undefined) fd.append(k, v) })
    if (logoFile.value) fd.append("logo", logoFile.value)
    if (faviconFile.value) fd.append("favicon", faviconFile.value)
    const { data } = await settingsApi.update(fd)
    settingsStore.applyTheme(data)
    saved.value = true; setTimeout(() => saved.value = false, 3000)
  } finally { saving.value = false }
}
onMounted(load)
</script>
<style scoped>.settings-tab{padding:9px 14px;border-radius:8px;cursor:pointer;font-size:13.5px;display:flex;align-items:center;transition:all .15s}.settings-tab:hover{background:var(--cos-bg)}.settings-tab.active{background:var(--cos-primary-light);color:var(--cos-primary);font-weight:600}</style>