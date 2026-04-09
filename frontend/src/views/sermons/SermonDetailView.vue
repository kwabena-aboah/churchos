<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">{{ sermon?.title }}</h1><p class="page-subtitle">{{ sermon?.speaker_detail?.name }} · {{ fmt(sermon?.date) }}</p></div><RouterLink to="/sermons" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left me-1"></i>Back</RouterLink></div>
    <div v-if="!sermon" class="cos-spinner"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-3">
      <div class="col-lg-8">
        <div class="cos-card mb-3">
          <div class="row g-2 mb-3">
            <div class="col-md-4"><div class="text-muted small">Scripture</div><div class="fw-semibold">{{ sermon.primary_scripture || "—" }}</div></div>
            <div class="col-md-4"><div class="text-muted small">Series</div><div class="fw-semibold">{{ sermon.series_detail?.title || "—" }}</div></div>
            <div class="col-md-4"><div class="text-muted small">Speaker</div><div class="fw-semibold">{{ sermon.speaker_detail?.name || "—" }}</div></div>
          </div>
          <p v-if="sermon.description" class="text-muted">{{ sermon.description }}</p>
          <div v-if="sermon.video_url" class="mb-3">
            <a :href="sermon.video_url" target="_blank" class="btn btn-sm btn-danger"><i class="bi bi-play-circle me-1"></i>Watch Video</a>
          </div>
          <div v-if="sermon.notes_pdf" class="mb-3">
            <a :href="sermon.notes_pdf" target="_blank" class="btn btn-sm btn-warning"><i class="bi bi-file-pdf me-1"></i>Download Notes</a>
          </div>
        </div>
        <div class="cos-card mb-3" v-if="sermon.ai_summary">
          <h6 class="fw-bold mb-2"><i class="bi bi-robot me-2 text-primary"></i>AI Summary</h6>
          <p class="mb-3">{{ sermon.ai_summary }}</p>
          <div v-if="sermon.ai_key_points?.length">
            <div class="fw-semibold small mb-2">Key Points:</div>
            <ul class="mb-0">
              <li v-for="p in sermon.ai_key_points" :key="p" class="mb-1 small">{{ p }}</li>
            </ul>
          </div>
        </div>
        <div class="cos-card" v-if="sermon.transcript">
          <h6 class="fw-bold mb-2">Transcript</h6>
          <div class="transcript-text">{{ sermon.transcript }}</div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="cos-card mb-3">
          <h6 class="fw-bold mb-3">AI Tools</h6>
          <div class="d-grid gap-2">
            <button class="btn btn-outline-primary btn-sm" @click="generateSummary" :disabled="aiLoading || !sermon.transcript"><span v-if="aiLoading" class="spinner-border spinner-border-sm me-2"></span><i v-else class="bi bi-robot me-2"></i>Generate AI Summary</button>
            <button class="btn btn-outline-secondary btn-sm" @click="transcribe" :disabled="aiLoading || !sermon.audio_file"><i class="bi bi-soundwave me-2"></i>Transcribe Audio</button>
          </div>
          <div v-if="!sermon.audio_file" class="text-muted small mt-2"><i class="bi bi-info-circle me-1"></i>Upload an audio file to enable transcription.</div>
          <div v-if="!sermon.transcript" class="text-muted small mt-1"><i class="bi bi-info-circle me-1"></i>Transcription required for AI summary.</div>
        </div>
        <div class="cos-card" v-if="sermon.ai_scriptures_extracted?.length">
          <h6 class="fw-bold mb-2">Referenced Scriptures</h6>
          <div v-for="s in sermon.ai_scriptures_extracted" :key="s" class="scripture-tag">{{ s }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import dayjs from "dayjs"
import { sermonsApi } from "@/api"
const route = useRoute()
const sermon = ref(null); const aiLoading = ref(false)
const fmt = d => d ? dayjs(d).format("DD MMM YYYY") : "—"
async function load() { const { data } = await sermonsApi.get(route.params.id); sermon.value = data }
async function generateSummary() { aiLoading.value = true; try { const { data } = await sermonsApi.generateSummary(route.params.id); sermon.value = { ...sermon.value, ...data } } finally { aiLoading.value = false } }
async function transcribe() { aiLoading.value = true; try { await sermonsApi.transcribe(route.params.id); await load() } finally { aiLoading.value = false } }
onMounted(load)
</script>
<style scoped>.transcript-text{max-height:300px;overflow-y:auto;font-size:13px;line-height:1.8;color:var(--cos-text-muted);background:var(--cos-bg);padding:12px;border-radius:8px}.scripture-tag{display:inline-block;background:var(--cos-primary-light);color:var(--cos-primary);padding:2px 8px;border-radius:4px;font-size:12px;margin:3px 3px 3px 0;font-weight:600}</style>