import { ref } from 'vue'

const toasts = ref([])
let idCounter = 0

export function useToast() {
  function add(message, type = 'success', duration = 4000) {
    const id = ++idCounter
    toasts.value.push({ id, message, type })
    setTimeout(() => remove(id), duration)
  }

  function remove(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx > -1) toasts.value.splice(idx, 1)
  }

  function success(msg) { add(msg, 'success') }
  function error(msg) { add(msg, 'danger', 6000) }
  function warning(msg) { add(msg, 'warning') }
  function info(msg) { add(msg, 'info') }

  return { toasts, add, remove, success, error, warning, info }
}

export { toasts }
