import { defineStore } from 'pinia'
import { ref } from 'vue'
import { settingsApi } from '@/api'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    church_name: 'ChurchOS',
    church_tagline: '',
    primary_color: '#1a6b3c',
    secondary_color: '#2c2c2c',
    accent_color: '#c9a84c',
    currency_code: 'GHS',
    currency_symbol: '₵',
    logo_url: null,
    enable_ai_features: false,
  })
  const loaded = ref(false)

  async function loadPublic() {
    if (loaded.value) return
    try {
      const { data } = await settingsApi.getPublic()
      settings.value = { ...settings.value, ...data }
      applyTheme(data)
      loaded.value = true
      // Update document title
      document.title = data.church_name || 'ChurchOS'
    } catch {}
  }

  function applyTheme(s) {
    const root = document.documentElement
    if (s.primary_color) root.style.setProperty('--cos-primary', s.primary_color)
    if (s.secondary_color) root.style.setProperty('--cos-secondary', s.secondary_color)
    if (s.accent_color) root.style.setProperty('--cos-accent', s.accent_color)
    // Derive dark shade
    root.style.setProperty('--cos-sidebar-bg', s.secondary_color || '#1a1a2e')
  }

  function formatCurrency(amount) {
    const sym = settings.value.currency_symbol || '₵'
    const num = parseFloat(amount || 0)
    return `${sym}${num.toLocaleString('en-GH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }

  return { settings, loaded, loadPublic, applyTheme, formatCurrency }
})
