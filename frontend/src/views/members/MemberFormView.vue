<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ isEdit ? 'Edit Member' : 'Add New Member' }}</h1>
        <p class="page-subtitle">{{ isEdit ? `Updating ${member.first_name} ${member.last_name}` : 'Register a new member or visitor' }}</p>
      </div>
      <RouterLink to="/members" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Back</RouterLink>
    </div>

    <form @submit.prevent="handleSubmit">
      <div class="row g-3">
        <!-- Left column -->
        <div class="col-lg-8">
          <div class="cos-card mb-3">
            <div class="form-section-title">Personal Information</div>
            <div class="row g-3">
              <div class="col-md-3">
                <label class="form-label">First Name *</label>
                <input v-model="member.first_name" class="form-control" required />
              </div>
              <div class="col-md-3">
                <label class="form-label">Middle Name</label>
                <input v-model="member.middle_name" class="form-control" />
              </div>
              <div class="col-md-3">
                <label class="form-label">Last Name *</label>
                <input v-model="member.last_name" class="form-control" required />
              </div>
              <div class="col-md-3">
                <label class="form-label">Preferred Name</label>
                <input v-model="member.preferred_name" class="form-control" />
              </div>
              <div class="col-md-3">
                <label class="form-label">Gender *</label>
                <select v-model="member.gender" class="form-select" required>
                  <option value="">Select</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Date of Birth</label>
                <input v-model="member.date_of_birth" type="date" class="form-control" />
              </div>
              <div class="col-md-3">
                <label class="form-label">Marital Status</label>
                <select v-model="member.marital_status" class="form-select">
                  <option value="">Select</option>
                  <option value="single">Single</option>
                  <option value="married">Married</option>
                  <option value="widowed">Widowed</option>
                  <option value="divorced">Divorced</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Occupation</label>
                <input v-model="member.occupation" class="form-control" />
              </div>
            </div>

            <div class="form-section-title">Contact Details</div>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Primary Phone *</label>
                <input v-model="member.phone_primary" class="form-control" required />
              </div>
              <div class="col-md-4">
                <label class="form-label">Secondary Phone</label>
                <input v-model="member.phone_secondary" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">WhatsApp Number</label>
                <input v-model="member.whatsapp_number" class="form-control" placeholder="If different from primary" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Email Address</label>
                <input v-model="member.email" type="email" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Address</label>
                <input v-model="member.address" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">City</label>
                <input v-model="member.city" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Region</label>
                <input v-model="member.region" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Country</label>
                <input v-model="member.country" class="form-control" />
              </div>
            </div>

            <div class="form-section-title">Membership Details</div>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Membership Status *</label>
                <select v-model="member.membership_status" class="form-select" required>
                  <option value="visitor">Visitor</option>
                  <option value="active">Active Member</option>
                  <option value="inactive">Inactive</option>
                  <option value="transferred_in">Transferred In</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Membership Date</label>
                <input v-model="member.membership_date" type="date" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Visitor Date</label>
                <input v-model="member.visitor_date" type="date" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Zone</label>
                <select v-model="member.zone" class="form-select">
                  <option :value="null">None</option>
                  <option v-for="z in zones" :key="z.id" :value="z.id">{{ z.name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Cell Group</label>
                <select v-model="member.cell_group" class="form-select">
                  <option :value="null">None</option>
                  <option v-for="g in cellGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
                </select>
              </div>
            </div>

            <div class="form-section-title">Spiritual Information</div>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Salvation Date</label>
                <input v-model="member.salvation_date" type="date" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Baptism Date</label>
                <input v-model="member.baptism_date" type="date" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Baptism Type</label>
                <input v-model="member.baptism_type" class="form-control" placeholder="Water, Holy Spirit…" />
              </div>
              <div class="col-12">
                <label class="form-label">Ministry Interests</label>
                <input v-model="member.ministry_interests" class="form-control" placeholder="Music, Ushering, Evangelism…" />
              </div>
            </div>

            <div class="form-section-title">Emergency Contact</div>
            <div class="row g-3">
              <div class="col-md-4">
                <label class="form-label">Contact Name</label>
                <input v-model="member.emergency_contact_name" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Contact Phone</label>
                <input v-model="member.emergency_contact_phone" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Relationship</label>
                <input v-model="member.emergency_contact_relationship" class="form-control" placeholder="Spouse, Parent, Sibling…" />
              </div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="col-lg-4">
          <div class="cos-card mb-3">
            <div class="form-section-title mt-0">Profile Photo</div>
            <div class="photo-upload" @click="$refs.photoInput.click()">
              <img v-if="photoPreview" :src="photoPreview" class="photo-preview" />
              <div v-else class="photo-placeholder">
                <i class="bi bi-camera"></i>
                <span>Click to upload photo</span>
              </div>
            </div>
            <input ref="photoInput" type="file" accept="image/*" class="d-none" @change="onPhoto" />
            <button v-if="photoPreview" type="button" class="btn btn-sm btn-outline-danger mt-2 w-100" @click="clearPhoto">
              <i class="bi bi-trash me-1"></i>Remove Photo
            </button>
          </div>

          <div class="cos-card mb-3">
            <div class="form-section-title mt-0">Communication Preferences</div>
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" v-model="member.receive_sms" id="rcvSms" />
              <label class="form-check-label" for="rcvSms">Receive SMS</label>
            </div>
            <div class="form-check mb-2">
              <input class="form-check-input" type="checkbox" v-model="member.receive_email" id="rcvEmail" />
              <label class="form-check-label" for="rcvEmail">Receive Email</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="member.receive_whatsapp" id="rcvWA" />
              <label class="form-check-label" for="rcvWA">Receive WhatsApp</label>
            </div>
          </div>

          <div class="cos-card mb-3">
            <div class="form-section-title mt-0">Notes (Internal)</div>
            <textarea v-model="member.notes" class="form-control" rows="4" placeholder="Pastoral notes, special needs…"></textarea>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div class="alert alert-danger" v-if="error">{{ error }}</div>

      <!-- Actions -->
      <div class="d-flex justify-content-end gap-2 mt-2 mb-4">
        <RouterLink to="/members" class="btn btn-outline-secondary">Cancel</RouterLink>
        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
          {{ saving ? 'Saving…' : (isEdit ? 'Save Changes' : 'Register Member') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { membersApi, settingsApi } from '@/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const member = ref({
  first_name: '', last_name: '', middle_name: '', preferred_name: '',
  gender: '', date_of_birth: '',
  phone_primary: '', email: '',
  address: '', city: '', region: '', country: 'Ghana',
  membership_status: 'visitor', membership_date: '', visitor_date: '',
  zone: null, cell_group: null,
  salvation_date: '', baptism_date: '',
  receive_sms: true, receive_email: true, receive_whatsapp: true,
})

const zones = ref([])
const cellGroups = ref([])
const saving = ref(false)
const error = ref('')
const photoPreview = ref(null)
const photoFile = ref(null)
const photoInput = ref(null)

function formatDate(val) {
  if (!val) return null
  if (/^\d{4}-\d{2}-\d{2}$/.test(val)) return val
  const d = new Date(val)
  return isNaN(d) ? null : d.toISOString().split('T')[0]
}

function buildPayload() {
  const hasFile = photoFile.value instanceof File

  const data = { ...member.value }

  // format dates
  const dateFields = [
    'date_of_birth',
    'membership_date',
    'visitor_date',
    'salvation_date',
    'baptism_date'
  ]

  function formatDate(val) {
    if (!val) return null
    if (/^\d{4}-\d{2}-\d{2}$/.test(val)) return val
    const d = new Date(val)
    return isNaN(d) ? null : d.toISOString().split('T')[0]
  }

  dateFields.forEach(f => {
    data[f] = formatDate(data[f])
  })

  // remove empty + invalid
  Object.keys(data).forEach(k => {
    if (data[k] === '' || data[k] === null || data[k] === undefined) {
      delete data[k]
    }
  })

  // remove invalid UUIDs
  if (!data.zone) delete data.zone
  if (!data.cell_group) delete data.cell_group

  // 🚫 CRITICAL: NEVER send photo unless it's a File
  delete data.photo

  // ✅ NO FILE → send JSON
  if (!hasFile) {
    return data
  }

  // ✅ FILE EXISTS → use FormData
  const fd = new FormData()

  Object.entries(data).forEach(([k, v]) => {
    fd.append(k, v)
  })

  fd.append('photo', photoFile.value) // only real file

  return fd
}

async function handleSubmit() {
  error.value = ''
  saving.value = true

  try {
    const payload = buildPayload()

    if (isEdit.value) {
      await membersApi.update(route.params.id, payload)
    } else {
      await membersApi.create(payload)
    }

    // 🔥 trigger refresh on list page
    router.push('/members?refresh=1')

  } catch (e) {
    const d = e.response?.data?.errors || e.response?.data
    error.value = d
      ? Object.values(d).flat().join(' | ')
      : 'Something went wrong'
  } finally {
    saving.value = false
  }
}

function onPhoto(e) {
  const f = e.target.files[0]
    if (f) photoFile.value = f
    photoPreview.value = URL.createObjectURL(f)
  }
function clearPhoto() { photoPreview.value = null; photoFile.value = null }

onMounted(async () => {
  const [z, g] = await Promise.all([
    settingsApi.getZones(),
    settingsApi.getCellGroups()
  ])

  zones.value = z.data.results || z.data
  cellGroups.value = g.data.results || g.data

  if (isEdit.value) {
    const { data } = await membersApi.get(route.params.id)

    Object.assign(member.value, data)

    // fix foreign keys
    member.value.zone = data.zone?.id || null
    member.value.cell_group = data.cell_group?.id || null
    // if (data.photo_url) photoPreview.value = data.photo_url
  }
})
</script>

<style scoped>
.photo-upload { cursor: pointer; border: 2px dashed var(--cos-border); border-radius: 10px; overflow: hidden; min-height: 160px; display: flex; align-items: center; justify-content: center; transition: border-color 0.2s; }
.photo-upload:hover { border-color: var(--cos-primary); }
.photo-preview { width: 100%; height: 200px; object-fit: cover; }
.photo-placeholder { text-align: center; color: var(--cos-text-muted); padding: 1.5rem; }
.photo-placeholder i { font-size: 2.5rem; display: block; margin-bottom: 8px; }
</style>
