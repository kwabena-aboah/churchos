<template>
  <div class="modal show d-block" tabindex="-1" @click.self="cancel">
    <div class="modal-dialog modal-dialog-centered modal-sm">
      <div class="modal-content">
        <div class="modal-header" :class="headerClass">
          <h6 class="modal-title mb-0">
            <i :class="`bi ${icon} me-2`"></i>{{ title }}
          </h6>
        </div>
        <div class="modal-body">
          <p class="mb-0">{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline-secondary btn-sm" @click="cancel">Cancel</button>
          <button :class="`btn btn-sm btn-${variant}`" @click="confirm">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </div>
  <div class="modal-backdrop show"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Confirm Action' },
  message: { type: String, default: 'Are you sure?' },
  confirmText: { type: String, default: 'Confirm' },
  variant: { type: String, default: 'danger' },
})

const emit = defineEmits(['confirm', 'cancel'])

const icon = computed(() => ({
  danger: 'bi-exclamation-triangle-fill',
  warning: 'bi-exclamation-circle-fill',
  success: 'bi-check-circle-fill',
  primary: 'bi-question-circle-fill',
}[props.variant] || 'bi-question-circle-fill'))

const headerClass = computed(() => `bg-${props.variant} text-white`)

function confirm() { emit('confirm') }
function cancel() { emit('cancel') }
</script>
