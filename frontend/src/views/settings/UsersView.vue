<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">System Users</h1><p class="page-subtitle">Manage who has access to ChurchOS</p></div><button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-person-plus me-1"></i>Add User</button></div>
    <div class="cos-card p-0">
      <div class="table-responsive"><table class="cos-table">
        <thead><tr><th>User</th><th>Role</th><th>Phone</th><th>Joined</th><th>Status</th><th></th></tr></thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td><div class="d-flex align-items-center gap-2"><div class="user-av">{{ initials(u.full_name) }}</div><div><div class="fw-semibold">{{ u.full_name }}</div><div class="text-muted" style="font-size:11px">{{ u.email }}</div></div></div></td>
            <td><span class="badge bg-primary-subtle text-primary">{{ u.role_label }}</span></td>
            <td>{{ u.phone || "—" }}</td>
            <td class="text-muted small">{{ fmt(u.date_joined) }}</td>
            <td><span class="status-badge" :class="u.is_active?'badge-active':'badge-inactive'">{{ u.is_active?"Active":"Inactive" }}</span></td>
            <td><button class="btn btn-xs btn-outline-primary" @click="openModal(u)"><i class="bi bi-pencil"></i></button></td>
          </tr>
        </tbody>
      </table></div>
    </div>
    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false"><div class="modal-dialog"><div class="modal-content">
      <div class="modal-header"><h5 class="modal-title">{{ editing?"Edit User":"Add User" }}</h5><button class="btn-close" @click="showModal=false"></button></div>
      <div class="modal-body">
        <div class="row g-3">
          <div class="col-6"><label class="form-label">First Name *</label><input v-model="form.first_name" class="form-control" required /></div>
          <div class="col-6"><label class="form-label">Last Name *</label><input v-model="form.last_name" class="form-control" required /></div>
          <div class="col-12"><label class="form-label">Email *</label><input v-model="form.email" type="email" class="form-control" required /></div>
          <div class="col-12"><label class="form-label">Role *</label><select v-model="form.role" class="form-select"><option value="super_admin">Super Admin</option><option value="administrator">Administrator</option><option value="finance_officer">Finance Officer</option><option value="pastor">Pastor / Overseer</option><option value="secretary">Secretary</option><option value="cell_leader">Cell Leader</option><option value="data_entry">Data Entry Clerk</option></select></div>
          <div class="col-12"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
          <div class="col-12" v-if="!editing"><label class="form-label">Password *</label><input v-model="form.password" type="password" class="form-control" required /></div>
          <div class="col-12" v-if="!editing"><label class="form-label">Confirm Password *</label><input v-model="form.confirm_password" type="password" class="form-control" required /></div>
        </div>
      </div>
      <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="save" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
    </div></div></div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { authApi } from "@/api"
const fmt = d => dayjs(d).format("DD MMM YYYY")
const initials = n => n?.split(" ").map(w=>w[0]).join("").toUpperCase().slice(0,2)||"?"
const users=ref([]); const showModal=ref(false); const editing=ref(null); const saving=ref(false)
const form=ref({first_name:"",last_name:"",email:"",role:"data_entry",phone:"",password:"",confirm_password:""})
async function load(){const{data}=await authApi.getUsers();users.value=data.results||data}
function openModal(u=null){editing.value=u;form.value=u?{...u,password:"",confirm_password:""}:{first_name:"",last_name:"",email:"",role:"data_entry",phone:"",password:"",confirm_password:""};showModal.value=true}
async function save(){saving.value=true;try{editing.value?await authApi.updateUser(editing.value.id,form.value):await authApi.createUser(form.value);showModal.value=false;load()}finally{saving.value=false}}
onMounted(load)
</script>
<style scoped>.user-av{width:36px;height:36px;border-radius:50%;background:var(--cos-primary-light);color:var(--cos-primary);font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;flex-shrink:0}.btn-xs{padding:2px 7px;font-size:11px}</style>