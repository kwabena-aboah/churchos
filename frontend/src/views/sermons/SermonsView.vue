<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div><h1 class="page-title">Sermons</h1><p class="page-subtitle">{{ sermons.length }} archived sermons</p></div>
      <button class="btn btn-primary btn-sm" @click="openModal()"><i class="bi bi-plus me-1"></i>Add Sermon</button>
    </div>
    <div class="cos-card mb-3">
      <div class="row g-2">
        <div class="col-md-4"><input v-model="search" type="text" class="form-control form-control-sm" placeholder="Search title, scripture…" @input="debouncedLoad" /></div>
        <div class="col-md-3"><select v-model="seriesFilter" class="form-select form-select-sm" @change="load"><option value="">All Series</option><option v-for="s in series" :key="s.id" :value="s.id">{{ s.title }}</option></select></div>
        <div class="col-md-3"><select v-model="speakerFilter" class="form-select form-select-sm" @change="load"><option value="">All Speakers</option><option v-for="s in speakers" :key="s.id" :value="s.id">{{ s.name }}</option></select></div>
      </div>
    </div>
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="s in sermons" :key="s.id">
        <div class="cos-card sermon-card h-100">
          <div class="d-flex justify-content-between mb-2">
            <span class="text-muted small">{{ fmt(s.date) }}</span>
            <div class="d-flex gap-1">
              <i class="bi bi-soundwave text-primary" v-if="s.has_audio" title="Audio available"></i>
              <i class="bi bi-play-circle text-danger" v-if="s.has_video" title="Video available"></i>
              <i class="bi bi-file-pdf text-warning" v-if="s.has_notes" title="Notes available"></i>
            </div>
          </div>
          <h6 class="fw-bold mb-1">{{ s.title }}</h6>
          <div class="text-muted small mb-1" v-if="s.speaker_name"><i class="bi bi-mic me-1"></i>{{ s.speaker_name }}</div>
          <div class="text-muted small mb-2" v-if="s.primary_scripture"><i class="bi bi-book me-1"></i>{{ s.primary_scripture }}</div>
          <div class="d-flex gap-1 flex-wrap mb-2">
            <span class="badge bg-primary-subtle text-primary" v-for="t in (s.topics||[]).slice(0,3)" :key="t">{{ t }}</span>
          </div>
          <RouterLink :to="`/sermons/${s.id}`" class="btn btn-sm btn-outline-primary w-100">View Details</RouterLink>
        </div>
      </div>
      <div class="col-12" v-if="sermons.length===0&&!loading">
        <div class="cos-card cos-empty"><i class="bi bi-mic"></i><p>No sermons archived yet.</p></div>
      </div>
    </div>

    <div class="modal show d-block" v-if="showModal" @click.self="showModal=false">
      <div class="modal-dialog modal-lg"><div class="modal-content">
        <div class="modal-header"><h5 class="modal-title">Add Sermon</h5><button class="btn-close" @click="showModal=false"></button></div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-12"><label class="form-label">Title *</label><input v-model="form.title" class="form-control" required /></div>
            <div class="col-md-4"><label class="form-label">Date *</label><input v-model="form.date" type="date" class="form-control" required /></div>
            <div class="col-md-4"><label class="form-label">Speaker</label><select v-model="form.speaker" class="form-select"><option :value="null">Select</option><option v-for="s in speakers" :key="s.id" :value="s.id">{{ s.name }}</option></select></div>
            <div class="col-md-4"><label class="form-label">Series</label><select v-model="form.series" class="form-select"><option :value="null">None</option><option v-for="s in series" :key="s.id" :value="s.id">{{ s.title }}</option></select></div>
            <div class="col-md-6"><label class="form-label">Primary Scripture</label><input v-model="form.primary_scripture" class="form-control" placeholder="e.g. John 3:16" /></div>
            <div class="col-md-6"><label class="form-label">Video URL</label><input v-model="form.video_url" type="url" class="form-control" placeholder="YouTube/Vimeo URL" /></div>
            <div class="col-12"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="2"></textarea></div>
            <div class="col-md-6"><label class="form-label">Notes PDF</label><input type="file" class="form-control" @change="e=>noteFile=e.target.files[0]" accept=".pdf" /></div>
            <div class="col-md-6"><label class="form-label">Audio File</label><input type="file" class="form-control" @change="e=>audioFile=e.target.files[0]" accept="audio/*" /></div>
          </div>
        </div>
        <div class="modal-footer"><button class="btn btn-outline-secondary" @click="showModal=false">Cancel</button><button class="btn btn-primary" @click="saveSermon" :disabled="saving"><span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>Save</button></div>
      </div></div>
    </div>
    <div class="modal-backdrop show" v-if="showModal"></div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { sermonsApi } from '@/api'
const sermons=ref([]); const series=ref([]); const speakers=ref([]); const loading=ref(false)
const search=ref(''); const seriesFilter=ref(''); const speakerFilter=ref('')
const showModal=ref(false); const saving=ref(false)
const form=ref({ title:'', date:dayjs().format('YYYY-MM-DD'), speaker:null, series:null, primary_scripture:'', video_url:'', description:'' })
const noteFile=ref(null); const audioFile=ref(null)
const fmt=d=>dayjs(d).format('DD MMM YYYY')
let dt; function debouncedLoad(){clearTimeout(dt);dt=setTimeout(load,400)}
async function load(){loading.value=true;const p={};if(search.value)p.search=search.value;if(seriesFilter.value)p.series=seriesFilter.value;if(speakerFilter.value)p.speaker=speakerFilter.value;const{data}=await sermonsApi.list(p);sermons.value=data.results||data;loading.value=false}
function openModal(){form.value={title:'',date:dayjs().format('YYYY-MM-DD'),speaker:null,series:null,primary_scripture:'',video_url:'',description:''};showModal.value=true}
async function saveSermon(){saving.value=true;try{const fd=new FormData();Object.entries(form.value).forEach(([k,v])=>{if(v!==null&&v!=='')fd.append(k,v)});if(noteFile.value)fd.append('notes_pdf',noteFile.value);if(audioFile.value)fd.append('audio_file',audioFile.value);await sermonsApi.create(fd);showModal.value=false;load()}finally{saving.value=false}}
onMounted(async()=>{const[s,sp]=await Promise.all([sermonsApi.getSeries(),sermonsApi.getSpeakers()]);series.value=s.data.results||s.data;speakers.value=sp.data.results||sp.data;load()})
</script>
<style scoped>.sermon-card{transition:all .2s}.sermon-card:hover{box-shadow:var(--cos-shadow-lg);transform:translateY(-2px)}</style>
