<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- ── Sidebar ── -->
    <aside class="app-sidebar" :class="{ open: mobileSidebarOpen }">
      <div class="sidebar-brand">
        <img v-if="settings.logo_url" :src="settings.logo_url" class="brand-logo" alt="Logo" />
        <i v-else class="bi bi-building brand-icon"></i>
        <div class="brand-text" v-show="!sidebarCollapsed">
          <span class="brand-name">{{ settings.church_name }}</span>
          <span class="brand-sub">Management</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label" v-show="!sidebarCollapsed">Overview</div>
        <SidebarItem icon="bi-speedometer2" label="Dashboard" to="/dashboard" />

        <div class="nav-section-label" v-show="!sidebarCollapsed">Church</div>
        <SidebarItem icon="bi-people-fill" label="Members" to="/members" />
        <SidebarItem icon="bi-calendar-event" label="Events" to="/events" />
        <SidebarItem icon="bi-chat-heart" label="Follow-Up" to="/followup" />
        <SidebarItem icon="bi-mic-fill" label="Sermons" to="/sermons" />
        <SidebarItem icon="bi-hand-thumbs-up" label="Prayer" to="/prayer" />
        <SidebarItem icon="bi-book" label="Discipleship" to="/discipleship" />

        <div class="nav-section-label" v-show="!sidebarCollapsed">Finance</div>
        <SidebarItem icon="bi-cash-coin" label="Transactions" to="/finance" />
        <SidebarItem icon="bi-heart-fill" label="Causes" to="/finance/causes" />
        <SidebarItem icon="bi-journal-check" label="Pledges" to="/finance/pledges" />
        <SidebarItem icon="bi-bar-chart-line" label="Budget" to="/budget" />

        <div class="nav-section-label" v-show="!sidebarCollapsed">Operations</div>
        <SidebarItem icon="bi-person-badge" label="Workers" to="/workers" />
        <SidebarItem icon="bi-wallet2" label="Payroll" to="/workers/payroll" />
        <SidebarItem icon="bi-box-seam" label="Inventory" to="/inventory" />
        <SidebarItem icon="bi-cart3" label="Procurement" to="/procurement" />
        <SidebarItem icon="bi-building-gear" label="Facility" to="/facility" />

        <div class="nav-section-label" v-show="!sidebarCollapsed">Tools</div>
        <SidebarItem icon="bi-megaphone" label="Messages" to="/communication" />
        <SidebarItem icon="bi-file-earmark-bar-graph" label="Reports" to="/reports" />
        <SidebarItem icon="bi-robot" label="AI Assistant" to="/ai" />
        <SidebarItem icon="bi-shield-check" label="Audit" to="/audit" />

        <template v-if="auth.canLevel(6)">
          <div class="nav-section-label" v-show="!sidebarCollapsed">Admin</div>
          <SidebarItem icon="bi-people" label="Users" to="/settings/users" />
          <SidebarItem icon="bi-gear-fill" label="Settings" to="/settings" />
        </template>
      </nav>

      <div class="sidebar-footer">
        <button class="collapse-btn" @click="toggleSidebar" :title="sidebarCollapsed ? 'Expand' : 'Collapse'">
          <i :class="sidebarCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'"></i>
        </button>
      </div>
    </aside>

    <!-- ── Mobile overlay ── -->
    <div class="sidebar-overlay" v-if="mobileSidebarOpen" @click="mobileSidebarOpen = false"></div>

    <!-- ── Main area ── -->
    <div class="app-main">
      <!-- Topbar -->
      <header class="app-topbar">
        <button class="topbar-menu-btn d-lg-none" @click="mobileSidebarOpen = true">
          <i class="bi bi-list"></i>
        </button>
        <div class="topbar-search d-none d-md-flex">
          <i class="bi bi-search"></i>
          <input type="text" placeholder="Search members, transactions…" v-model="searchQuery" @keyup.enter="doSearch" />
        </div>
        <div class="topbar-right">
          <!-- Birthday bell -->
          <button class="topbar-btn" title="Birthdays Today" @click="showBirthdays = true">
            <i class="bi bi-balloon-heart"></i>
            <span class="topbar-badge" v-if="birthdayCount">{{ birthdayCount }}</span>
          </button>
          <!-- Notifications -->
          <button class="topbar-btn" title="Notifications">
            <i class="bi bi-bell"></i>
          </button>
          <!-- User menu -->
          <div class="topbar-user dropdown">
            <button class="dropdown-toggle d-flex align-items-center gap-2" data-bs-toggle="dropdown">
              <div class="user-avatar">{{ initials }}</div>
              <span class="d-none d-md-inline">{{ auth.userFullName }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><span class="dropdown-item-text fw-bold">{{ auth.userFullName }}</span></li>
              <li><span class="dropdown-item-text text-muted small">{{ auth.userRole?.replace('_', ' ') }}</span></li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink class="dropdown-item" to="/profile"><i class="bi bi-person me-2"></i>Profile</RouterLink></li>
              <li><RouterLink class="dropdown-item" to="/settings" v-if="auth.canLevel(6)"><i class="bi bi-gear me-2"></i>Settings</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><button class="dropdown-item text-danger" @click="handleLogout"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></li>
            </ul>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="app-content">
        <RouterView v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
    </div>

    <!-- Birthdays modal -->
    <BirthdayModal v-if="showBirthdays" @close="showBirthdays = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { membersApi } from '@/api'
import SidebarItem from './SidebarItem.vue'
import BirthdayModal from '../common/BirthdayModal.vue'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const settings = settingsStore.settings

const sidebarCollapsed = ref(false)
const mobileSidebarOpen = ref(false)
const searchQuery = ref('')
const showBirthdays = ref(false)
const birthdayCount = ref(0)

const initials = computed(() => {
  const name = auth.userFullName || ''
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

function toggleSidebar() { sidebarCollapsed.value = !sidebarCollapsed.value }

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ name: 'members', query: { search: searchQuery.value } })
  }
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

onMounted(async () => {
  try {
    const { data } = await membersApi.birthdaysToday()
    birthdayCount.value = data.count || (Array.isArray(data) ? data.length : 0)
  } catch {}
})
</script>

<style scoped>
.app-shell { display: flex; min-height: 100vh; }

/* ── Sidebar ── */
.app-sidebar {
  width: var(--cos-sidebar-width);
  background: var(--cos-sidebar-bg);
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; bottom: 0;
  z-index: 1000;
  transition: width 0.25s ease;
  overflow: hidden;
}
.sidebar-collapsed .app-sidebar { width: 64px; }

.sidebar-brand {
  display: flex; align-items: center; gap: 10px;
  padding: 18px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  min-height: 64px;
}
.brand-logo { width: 36px; height: 36px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.brand-icon { font-size: 28px; color: var(--cos-accent); flex-shrink: 0; }
.brand-name { font-size: 15px; font-weight: 700; color: #fff; display: block; white-space: nowrap; }
.brand-sub { font-size: 11px; color: rgba(255,255,255,0.4); display: block; }

.sidebar-nav { flex: 1; overflow-y: auto; padding: 8px 0; }
.nav-section-label {
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em;
  color: rgba(255,255,255,0.3); padding: 12px 16px 4px;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255,255,255,0.08);
  display: flex; justify-content: flex-end;
}
.collapse-btn {
  background: rgba(255,255,255,0.08); border: none;
  color: rgba(255,255,255,0.6); width: 28px; height: 28px;
  border-radius: 6px; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  transition: all 0.2s;
}
.collapse-btn:hover { background: rgba(255,255,255,0.15); color: #fff; }

.sidebar-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  z-index: 999; display: none;
}

/* ── Main ── */
.app-main {
  flex: 1;
  margin-left: var(--cos-sidebar-width);
  transition: margin-left 0.25s ease;
  display: flex; flex-direction: column;
  min-width: 0;
}
.sidebar-collapsed .app-main { margin-left: 64px; }

/* ── Topbar ── */
.app-topbar {
  height: var(--cos-topbar-height);
  background: var(--cos-card-bg);
  border-bottom: 1px solid var(--cos-border);
  display: flex; align-items: center;
  padding: 0 1.5rem; gap: 1rem;
  position: sticky; top: 0; z-index: 100;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.topbar-menu-btn {
  background: none; border: none; font-size: 22px;
  cursor: pointer; color: var(--cos-text);
}
.topbar-search {
  flex: 1; max-width: 340px;
  display: flex; align-items: center; gap: 8px;
  background: var(--cos-bg); border-radius: 8px;
  padding: 6px 12px; border: 1px solid var(--cos-border);
}
.topbar-search i { color: var(--cos-text-muted); font-size: 14px; }
.topbar-search input { border: none; background: none; outline: none; font-size: 13px; flex: 1; }

.topbar-right { margin-left: auto; display: flex; align-items: center; gap: 6px; }
.topbar-btn {
  position: relative; background: none; border: none;
  width: 36px; height: 36px; border-radius: 8px;
  cursor: pointer; font-size: 16px; color: var(--cos-text-muted);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.topbar-btn:hover { background: var(--cos-bg); color: var(--cos-primary); }
.topbar-badge {
  position: absolute; top: 3px; right: 3px;
  background: var(--cos-danger); color: white;
  font-size: 9px; font-weight: 700;
  width: 16px; height: 16px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.topbar-user button {
  background: none; border: none; cursor: pointer;
  padding: 4px 8px; border-radius: 8px;
  transition: background 0.2s;
}
.topbar-user button:hover { background: var(--cos-bg); }
.topbar-user .dropdown-toggle::after { display: none; }
.user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--cos-primary); color: white;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ── Content ── */
.app-content { flex: 1; padding: 1.5rem; overflow-x: hidden; }

/* ── Page transitions ── */
.page-enter-active, .page-leave-active { transition: all 0.18s ease; }
.page-enter-from { opacity: 0; transform: translateY(8px); }
.page-leave-to { opacity: 0; }

/* ── Mobile ── */
@media (max-width: 768px) {
  .app-sidebar { transform: translateX(-100%); width: 260px !important; }
  .app-sidebar.open { transform: translateX(0); }
  .sidebar-overlay { display: block; }
  .app-main { margin-left: 0 !important; }
  .app-content { padding: 1rem; }
}
</style>
