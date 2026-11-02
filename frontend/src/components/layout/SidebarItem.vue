<template>
  <RouterLink :to="to" class="sidebar-link" :class="{ active: isActive }" :title="label">
    <i :class="`bi ${icon}`"></i>
    <span class="link-label">{{ label }}</span>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({ icon: String, label: String, to: String })
const route = useRoute()
const isActive = computed(() => {
  if (props.to === '/dashboard') return route.path === '/dashboard'
  return route.path.startsWith(props.to)
})
</script>

<style scoped>
.sidebar-link {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 16px;
  color: var(--cos-sidebar-text);
  text-decoration: none;
  border-radius: 0;
  transition: all 0.15s;
  white-space: nowrap;
  font-size: 13.5px;
  border-left: 3px solid transparent;
}
.sidebar-link i { font-size: 16px; width: 20px; text-align: center; flex-shrink: 0; }
.sidebar-link:hover {
  background: rgba(255,255,255,0.07);
  color: rgba(255,255,255,0.95);
}
.sidebar-link.active {
  background: rgba(255,255,255,0.12);
  color: #fff;
  border-left-color: var(--cos-accent);
  font-weight: 600;
}
.sidebar-link.active i { color: var(--cos-accent); }
</style>
