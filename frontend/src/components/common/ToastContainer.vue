<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show align-items-center"
      :class="`text-bg-${toast.type}`"
      role="alert"
    >
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i :class="`bi ${iconFor(toast.type)}`"></i>
          {{ toast.message }}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="remove(toast.id)"></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { toasts, useToast } from '@/composables/useToast'

const { remove } = useToast()

function iconFor(type) {
  return {
    success: 'bi-check-circle-fill',
    danger: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill',
  }[type] || 'bi-info-circle-fill'
}
</script>
