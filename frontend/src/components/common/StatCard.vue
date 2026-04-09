<template>
  <div class="stat-card" @click="$emit('click')">
    <div class="stat-icon" :style="{ background: iconBg }">
      <i :class="`bi ${icon}`" :style="{ color: iconColor }"></i>
    </div>
    <div class="flex-grow-1">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
      <div v-if="trend !== null" class="stat-trend" :class="trend >= 0 ? 'text-success' : 'text-danger'">
        <i :class="`bi bi-arrow-${trend >= 0 ? 'up' : 'down'}`"></i>
        {{ Math.abs(trend) }}% vs last month
      </div>
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'bi-graph-up' },
  iconBg: { type: String, default: '#e8f5ee' },
  iconColor: { type: String, default: '#1a6b3c' },
  value: { type: [String, Number], default: '—' },
  label: { type: String, default: '' },
  trend: { type: Number, default: null },
})
defineEmits(['click'])
</script>
