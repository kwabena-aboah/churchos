<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Members</h1><p class="page-subtitle">{{ pagination.count }} total members</p></div>
      <div class="d-flex gap-2 flex-wrap">
        <button class="btn btn-outline-secondary btn-sm" @click="exportMembers"><i class="bi bi-download me-1"></i>Export</button>
        <RouterLink to="/members/new" class="btn btn-primary btn-sm"><i class="bi bi-person-plus me-1"></i>Add Member</RouterLink>
      </div>
    </div>

    <!-- Filters -->
    <div class="cos-card mb-3">
      <div class="row g-2">
        <div class="col-md-4">
          <div class="input-group input-group-sm">
            <span class="input-group-text"><i class="bi bi-search"></i></span>
            <input v-model="filters.search" type="text" class="form-control" placeholder="Search name, phone, email…" @input="debouncedLoad" />
          </div>
        </div>
        <div class="col-md-2">
          <select v-model="filters.membership_status" class="form-select form-select-sm" @change="loadMembers">
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="visitor">Visitor</option>
            <option value="inactive">Inactive</option>
            <option value="transferred_out">Transferred Out</option>
          </select>
        </div>
        <div class="col-md-2">
          <select v-model="filters.gender" class="form-select form-select-sm" @change="loadMembers">
            <option value="">All Genders</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <div class="col-md-2">
          <select v-model="filters.zone" class="form-select form-select-sm" @change="loadMembers">
            <option value="">All Zones</option>
            <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.name }}</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary btn-sm w-100" @click="clearFilters">
            <i class="bi bi-x-circle me-1"></i>Clear
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="cos-card p-0">
      <div v-if="loading" class="cos-spinner p-5"><div class="spinner-border text-primary"></div><span>Loading members…</span></div>
      <div v-else-if="members.length === 0" class="cos-empty p-5">
        <i class="bi bi-people"></i><p>No members found</p>
        <RouterLink to="/members/new" class="btn btn-primary btn-sm">Add First Member</RouterLink>
      </div>
      <div v-else class="table-responsive">
        <table class="cos-table">
          <thead>
            <tr>
              <th><input type="checkbox" @change="toggleAll" :checked="allSelected" /></th>
              <th>Member</th>
              <th>Number</th>
              <th>Phone</th>
              <th>Status</th>
              <th>Zone / Cell</th>
              <th>Joined</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in members" :key="m.id">
              <td><input type="checkbox" v-model="selected" :value="m.id" /></td>
              <td>
                <div class="d-flex align-items-center gap-2">
                  <div class="member-avatar">{{ initials(m.full_name) }}</div>
                  <div>
                    <div class="fw-semibold">{{ m.full_name }}</div>
                    <div class="text-muted" style="font-size:11px">{{ m.email || '—' }}</div>
                  </div>
                </div>
              </td>
              <td><code class="text-primary">{{ m.member_number }}</code></td>
              <td>{{ m.phone_primary }}</td>
              <td>
                <span class="status-badge" :class="statusClass(m.membership_status)">
                  {{ m.membership_status }}
                </span>
              </td>
              <td>
                <div>{{ m.zone_name || '—' }}</div>
                <div class="text-muted" style="font-size:11px">{{ m.cell_group_name || '' }}</div>
              </td>
              <td class="text-muted">{{ formatDate(m.created_at) }}</td>
              <td>
                <div class="d-flex gap-1">
                  <RouterLink :to="`/members/${m.id}`" class="btn btn-xs btn-outline-primary" title="View"><i class="bi bi-eye"></i></RouterLink>
                  <RouterLink :to="`/members/${m.id}/edit`" class="btn btn-xs btn-outline-secondary" title="Edit"><i class="bi bi-pencil"></i></RouterLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="d-flex align-items-center justify-content-between p-3 border-top" v-if="pagination.total_pages > 1">
        <span class="text-muted small">Page {{ pagination.current_page }} of {{ pagination.total_pages }} ({{ pagination.count }} members)</span>
        <div class="d-flex gap-1">
          <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.previous" @click="goPage(pagination.current_page - 1)">
            <i class="bi bi-chevron-left"></i>
          </button>
          <button v-for="p in pageNumbers" :key="p" class="btn btn-sm"
            :class="p === pagination.current_page ? 'btn-primary' : 'btn-outline-secondary'"
            @click="goPage(p)">{{ p }}</button>
          <button class="btn btn-sm btn-outline-secondary" :disabled="!pagination.next" @click="goPage(pagination.current_page + 1)">
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { membersApi, settingsApi } from '@/api'
import { emitter } from '@/eventBus'

const route = useRoute()
const members = ref([])
const zones = ref([])
const loading = ref(false)
const selected = ref([])
const filters = ref({ search: route.query.search || '', membership_status: '', gender: '', zone: '' })
const pagination = ref({ count: 0, total_pages: 1, current_page: 1, next: null, previous: null })

const allSelected = computed(() => selected.value.length === members.value.length && members.value.length > 0)
const pageNumbers = computed(() => {
  const pages = []; const total = pagination.value.total_pages; const cur = pagination.value.current_page
  for (let i = Math.max(1, cur - 2); i <= Math.min(total, cur + 2); i++) pages.push(i)
  return pages
})

function initials(name) { return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?' }
function formatDate(d) { return dayjs(d).format('DD MMM YYYY') }
function statusClass(s) {
  return { active: 'badge-active', inactive: 'badge-inactive', visitor: 'badge-visitor', transferred_out: 'badge-pending' }[s] || 'badge-visitor'
}
function toggleAll(e) { selected.value = e.target.checked ? members.value.map(m => m.id) : [] }

let debounceTimer
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(loadMembers, 400) }

async function loadMembers(page = 1) {
  loading.value = true
  try {
    const params = { page:page, page_size: 25, ...Object.fromEntries(Object.entries(filters.value).filter(([_,v]) => v)) }
    const { data } = await membersApi.list(params)
    members.value = data.results ?? data
    if (data.count !== undefined) {
      pagination.value = { count: data.count, total_pages: data.total_pages, current_page: data.current_page, next: data.next, previous: data.previous }
    }
  } catch (error) {
    console.error("Fetch error:", error.response?.data || error);
  } finally { loading.value = false }
}

function goPage(p) { if (p >= 1 && p <= pagination.value.total_pages) loadMembers(p) }
function clearFilters() { filters.value = { search: '', membership_status: '', gender: '', zone: '' }; loadMembers() }

async function exportMembers() {
  alert('Export feature: implement CSV download via backend /members/export/ endpoint.')
}

onMounted(async () => {
  const { data } = await settingsApi.getZones()
  zones.value = data.results || data
  loadMembers()
  
  emitter.on('member-updated', () => {
    loadMembers()
  })
})

watch(() => route.query.refresh, (val) => {
  if (val) {
    loadMembers()
  }
})
</script>

<style scoped>
.member-avatar { width:36px;height:36px;border-radius:50%;background:var(--cos-primary-light);color:var(--cos-primary);font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;flex-shrink:0; }
.btn-xs { padding:2px 7px;font-size:11px; }
</style>
