<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">My Profile</h1></div></div>
    <div class="row g-3">
      <div class="col-lg-5">
        <div class="cos-card text-center">
          <div class="profile-avatar mx-auto mb-3">{{ initials }}</div>
          <h5 class="fw-bold">{{ auth.userFullName }}</h5>
          <p class="text-muted">{{ auth.user?.email }}</p>
          <span class="badge bg-primary-subtle text-primary fs-6">{{ auth.user?.role_label }}</span>
        </div>
      </div>
      <div class="col-lg-7">
        <div class="cos-card mb-3">
          <h6 class="fw-bold mb-3">Update Profile</h6>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label">First Name</label><input v-model="form.first_name" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Last Name</label><input v-model="form.last_name" class="form-control" /></div>
            <div class="col-12"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
          </div>
          <button class="btn btn-primary mt-3" @click="saveProfile" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save Profile</button>
        </div>
        <div class="cos-card">
          <h6 class="fw-bold mb-3">Change Password</h6>
          <div class="mb-3"><label class="form-label">Current Password</label><input v-model="pwd.old_password" type="password" class="form-control" /></div>
          <div class="mb-3"><label class="form-label">New Password</label><input v-model="pwd.new_password" type="password" class="form-control" /></div>
          <div class="mb-3"><label class="form-label">Confirm New Password</label><input v-model="pwd.confirm_new_password" type="password" class="form-control" /></div>
          <div class="alert alert-danger small" v-if="pwdError">{{ pwdError }}</div>
          <div class="alert alert-success small" v-if="pwdSuccess">Password changed successfully.</div>
          <button class="btn btn-outline-primary" @click="changePassword" :disabled="savingPwd">Change Password</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from "vue"
import { useAuthStore } from "@/stores/auth"
import { authApi } from "@/api"
const auth = useAuthStore()
const initials = computed(() => auth.userFullName?.split(" ").map(n=>n[0]).join("").toUpperCase().slice(0,2)||"?")
const form = ref({ first_name:"", last_name:"", phone:"" })
const pwd = ref({ old_password:"", new_password:"", confirm_new_password:"" })
const saving = ref(false); const savingPwd = ref(false); const pwdError = ref(""); const pwdSuccess = ref(false)
async function saveProfile() { saving.value=true; try { await authApi.me(); await auth.fetchMe() } finally { saving.value=false } }
async function changePassword() { pwdError.value=""; pwdSuccess.value=false; savingPwd.value=true; try { await authApi.changePassword(pwd.value); pwdSuccess.value=true; pwd.value={old_password:"",new_password:"",confirm_new_password:""} } catch(e) { pwdError.value=JSON.stringify(e.response?.data||"Error") } finally { savingPwd.value=false } }
onMounted(() => { form.value = { first_name: auth.user?.first_name||"", last_name: auth.user?.last_name||"", phone: auth.user?.phone||"" } })
</script>
<style scoped>.profile-avatar{width:80px;height:80px;border-radius:50%;background:var(--cos-primary);color:white;font-size:28px;font-weight:800;display:flex;align-items:center;justify-content:center}</style>