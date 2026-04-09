<template>
  <div class="modal show d-block" tabindex="-1" @click.self="$emit('close')">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title"><i class="bi bi-balloon-heart me-2"></i>Birthdays Today 🎂</h5>
          <button class="btn-close" @click="$emit('close')"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="cos-spinner"><div class="spinner-border text-primary"></div></div>
          <div v-else-if="members.length === 0" class="cos-empty">
            <i class="bi bi-emoji-smile"></i>
            <p>No birthdays today!</p>
          </div>
          <div v-else>
            <div v-for="m in members" :key="m.id" class="birthday-item">
              <div class="birthday-avatar">{{ initials(m.full_name) }}</div>
              <div>
                <div class="fw-semibold">{{ m.full_name }}</div>
                <div class="text-muted small">{{ m.phone_primary }} · {{ m.membership_status }}</div>
              </div>
              <span class="ms-auto badge bg-warning text-dark">🎂 Today</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop show"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { membersApi } from '@/api'

defineEmits(['close'])

const members = ref([])
const loading = ref(true)

const initials = (name) => name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?'

onMounted(async () => {
  try {
    const { data } = await membersApi.birthdaysToday()
    members.value = Array.isArray(data) ? data : (data.results || [])
  } catch {} finally { loading.value = false }
})
</script>

<style scoped>
.birthday-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid var(--cos-border);
}
.birthday-item:last-child { border-bottom: none; }
.birthday-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--cos-primary-light); color: var(--cos-primary);
  font-weight: 700; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
</style>
