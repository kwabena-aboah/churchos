<template>
  <div class="login-page">
    <div class="login-left d-none d-lg-flex">
      <div class="login-art">
        <div class="art-circle c1"></div>
        <div class="art-circle c2"></div>
        <div class="art-circle c3"></div>
      </div>
      <div class="login-brand-info">
        <div class="login-logo">
          <img v-if="settings.logo_url" :src="settings.logo_url" alt="Logo" />
          <i v-else class="bi bi-building"></i>
        </div>
        <h1>{{ settings.church_name }}</h1>
        <p>{{ settings.church_tagline || 'Church Management System' }}</p>
        <div class="login-features">
          <div class="feature-item" v-for="f in features" :key="f.text">
            <i :class="`bi ${f.icon}`"></i><span>{{ f.text }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-form-wrap">
        <div class="login-header d-lg-none">
          <i class="bi bi-building-fill text-success fs-2"></i>
          <h2>{{ settings.church_name }}</h2>
        </div>
        <h2 class="form-title">Welcome back</h2>
        <p class="form-subtitle">Sign in to your account to continue</p>

        <div class="alert alert-danger d-flex align-items-center gap-2" v-if="error">
          <i class="bi bi-exclamation-triangle-fill"></i>{{ error }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label">Email Address</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-envelope"></i></span>
              <input v-model="form.email" type="email" class="form-control" placeholder="you@church.org" required autocomplete="email" />
            </div>
          </div>
          <div class="mb-4">
            <label class="form-label">Password</label>
            <div class="input-group">
              <span class="input-group-text"><i class="bi bi-lock"></i></span>
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" class="form-control" placeholder="••••••••" required autocomplete="current-password" />
              <button type="button" class="input-group-text" @click="showPwd = !showPwd" style="cursor:pointer">
                <i :class="`bi ${showPwd ? 'bi-eye-slash' : 'bi-eye'}`"></i>
              </button>
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Signing in…' : 'Sign In' }}
          </button>
        </form>

        <p class="login-footer">ChurchOS &copy; {{ new Date().getFullYear() }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const settings = settingsStore.settings

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPwd = ref(false)

const features = [
  { icon: 'bi-people-fill', text: 'Member Management' },
  { icon: 'bi-cash-coin', text: 'Finance & Giving' },
  { icon: 'bi-calendar-event', text: 'Events & Attendance' },
  { icon: 'bi-robot', text: 'AI-Powered Insights' },
]

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.value.email, form.value.password)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid email or password.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { display: flex; min-height: 100vh; background: var(--cos-bg); }

.login-left {
  width: 44%; background: var(--cos-primary);
  flex-direction: column; align-items: center; justify-content: center;
  padding: 3rem; position: relative; overflow: hidden;
}
.art-circle { position: absolute; border-radius: 50%; opacity: 0.12; background: white; }
.c1 { width: 400px; height: 400px; top: -100px; right: -100px; }
.c2 { width: 250px; height: 250px; bottom: -50px; left: -80px; }
.c3 { width: 150px; height: 150px; top: 50%; left: 20%; }

.login-brand-info { position: relative; z-index: 1; text-align: center; color: white; }
.login-logo { width: 80px; height: 80px; border-radius: 20px; background: rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; font-size: 36px; }
.login-logo img { width: 60px; height: 60px; border-radius: 12px; object-fit: cover; }
.login-brand-info h1 { font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; }
.login-brand-info p { opacity: 0.8; margin-bottom: 2rem; }
.login-features { display: flex; flex-direction: column; gap: 12px; text-align: left; }
.feature-item { display: flex; align-items: center; gap: 12px; font-size: 14px; opacity: 0.9; }
.feature-item i { font-size: 18px; opacity: 0.7; }

.login-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; }
.login-form-wrap { width: 100%; max-width: 400px; }
.login-header { text-align: center; margin-bottom: 2rem; }
.form-title { font-size: 1.75rem; font-weight: 800; margin-bottom: 6px; }
.form-subtitle { color: var(--cos-text-muted); margin-bottom: 2rem; }
.login-footer { text-align: center; color: var(--cos-text-muted); font-size: 12px; margin-top: 2rem; }
</style>
