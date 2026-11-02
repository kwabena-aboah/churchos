<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">{{ member?.get_full_name || member?.full_name }}</h1><p class="page-subtitle">{{ member?.member_number }} · {{ member?.membership_status }}</p></div>
      <div class="d-flex gap-2">
        <RouterLink to="/members" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Back</RouterLink>
        <RouterLink :to="`/members/${$route.params.id}/edit`" class="btn btn-primary btn-sm"><i class="bi bi-pencil me-1"></i>Edit</RouterLink>
      </div>
    </div>
    <div v-if="!member" class="cos-spinner"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-3">
      <div class="col-lg-4">
        <div class="cos-card text-center mb-3">
          <img v-if="member.photo_url" :src="member.photo_url" class="member-photo mb-3" />
          <div v-else class="member-avatar-lg mx-auto mb-3">{{ initials(member.full_name) }}</div>
          <h5 class="fw-bold mb-0">{{ member.full_name }}</h5>
          <p class="text-muted mb-2">{{ member.occupation || "No occupation listed" }}</p>
          <span class="status-badge me-1" :class="statusClass(member.membership_status)">{{ member.membership_status }}</span>
          <span v-if="member.is_birthday_today" class="status-badge badge-warning">🎂 Birthday Today!</span>
          <div class="row text-center mt-3 pt-3 border-top">
            <div class="col-4"><div class="text-muted small">Age</div><div class="fw-bold">{{ member.age || "—" }}</div></div>
            <div class="col-4"><div class="text-muted small">Years Member</div><div class="fw-bold">{{ member.years_as_member || "—" }}</div></div>
            <div class="col-4"><div class="text-muted small">Cell Group</div><div class="fw-bold small">{{ member.cell_group_name || "—" }}</div></div>
          </div>
        </div>
        <div class="cos-card">
          <h6 class="fw-bold mb-3">Contact</h6>
          <div class="info-row"><i class="bi bi-telephone"></i><a :href="`tel:${member.phone_primary}`">{{ member.phone_primary }}</a></div>
          <div class="info-row" v-if="member.phone_secondary"><i class="bi bi-telephone-plus"></i><span>{{ member.phone_secondary }}</span></div>
          <div class="info-row" v-if="member.email"><i class="bi bi-envelope"></i><a :href="`mailto:${member.email}`">{{ member.email }}</a></div>
          <div class="info-row" v-if="member.address"><i class="bi bi-geo-alt"></i><span>{{ member.address }}, {{ member.city }}</span></div>
        </div>
      </div>
      <div class="col-lg-8">
        <ul class="nav nav-tabs mb-3">
          <li class="nav-item" v-for="t in tabs" :key="t"><a class="nav-link" :class="activeTab===t?'active':''" @click="activeTab=t" style="cursor:pointer">{{ t }}</a></li>
        </ul>
        <div class="cos-card" v-if="activeTab==='Spiritual'">
          <div class="row g-3">
            <div class="col-md-4"><div class="text-muted small">Salvation Date</div><div class="fw-semibold">{{ member.salvation_date || "—" }}</div></div>
            <div class="col-md-4"><div class="text-muted small">Baptism Date</div><div class="fw-semibold">{{ member.baptism_date || "—" }}</div></div>
            <div class="col-md-4"><div class="text-muted small">Baptism Type</div><div class="fw-semibold">{{ member.baptism_type || "—" }}</div></div>
            <div class="col-12"><div class="text-muted small">Ministry Interests</div><div>{{ member.ministry_interests || "—" }}</div></div>
          </div>
        </div>
        <div class="cos-card" v-if="activeTab==='Giving'">
          <div v-if="transactions.length === 0" class="cos-empty"><i class="bi bi-receipt"></i><p>No giving records.</p></div>
          <table class="cos-table" v-else>
            <thead><tr><th>Date</th><th>Type</th><th>Amount</th><th>Method</th><th>Receipt</th></tr></thead>
            <tbody>
              <tr v-for="t in transactions" :key="t.id">
                <td>{{ fmt(t.transaction_date) }}</td>
                <td><span class="status-badge badge-visitor">{{ t.transaction_type }}</span></td>
                <td class="fw-bold text-success">{{ fmtCur(t.amount) }}</td>
                <td class="text-muted small">{{ t.payment_method }}</td>
                <td><code class="small">{{ t.receipt_number }}</code></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="cos-card" v-if="activeTab==='Follow-Up'">
          <div v-if="followups.length===0" class="cos-empty"><i class="bi bi-chat-heart"></i><p>No follow-up cases.</p></div>
          <div v-for="c in followups" :key="c.id" class="followup-item">
            <div class="d-flex justify-content-between"><span class="fw-semibold">{{ c.case_type.replace("_"," ") }}</span><span class="status-badge" :class="c.status==='closed'?'badge-active':'badge-warning'">{{ c.status }}</span></div>
            <p class="text-muted small mb-0">{{ c.description }}</p>
          </div>
        </div>
        <div class="cos-card" v-if="activeTab==='Notes'">
          <div class="text-muted" v-if="!member.notes">No internal notes.</div>
          <p v-else>{{ member.notes }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import dayjs from "dayjs"
import { membersApi, financeApi, followupApi } from "@/api"
import { useSettingsStore } from "@/stores/settings"
const route = useRoute(); const settingsStore = useSettingsStore()
const fmtCur = v => settingsStore.formatCurrency(v)
const fmt = d => dayjs(d).format("DD MMM YYYY")
const initials = n => n?.split(" ").map(w=>w[0]).join("").toUpperCase().slice(0,2)||"?"
const statusClass = s => ({active:"badge-active",inactive:"badge-inactive",visitor:"badge-visitor",transferred_out:"badge-pending"}[s]||"badge-visitor")
const member = ref(null); const transactions = ref([]); const followups = ref([])
const activeTab = ref("Spiritual"); const tabs = ["Spiritual","Giving","Follow-Up","Notes"]
async function load() {
  const { data } = await membersApi.get(route.params.id); member.value = data
  const [txns, fups] = await Promise.all([financeApi.listTransactions({member:route.params.id,page_size:20}), followupApi.list({member:route.params.id})])
  transactions.value = txns.data.results||txns.data; followups.value = fups.data.results||fups.data
}
onMounted(load)
</script>
<style scoped>
.member-photo{width:100px;height:100px;border-radius:50%;object-fit:cover}
.member-avatar-lg{width:100px;height:100px;border-radius:50%;background:var(--cos-primary);color:white;font-size:32px;font-weight:800;display:flex;align-items:center;justify-content:center}
.info-row{display:flex;gap:10px;align-items:flex-start;padding:6px 0;border-bottom:1px solid var(--cos-border);font-size:13px}
.info-row i{color:var(--cos-primary);width:18px;flex-shrink:0;margin-top:2px}
.followup-item{padding:10px 0;border-bottom:1px solid var(--cos-border)}
.followup-item:last-child{border-bottom:none}
</style>