<template>
  <div class="fade-in-up">
    <div class="page-header"><div><h1 class="page-title">Self-Audit Engine</h1><p class="page-subtitle">Automated system integrity and financial checks</p></div><button class="btn btn-primary btn-sm" @click="runAll" :disabled="running"><span v-if="running" class="spinner-border spinner-border-sm me-2"></span><i v-else class="bi bi-play-fill me-1"></i>Run All Checks</button></div>
    <div class="row g-3 mb-4" v-if="summary">
      <div class="col-md-4"><div class="stat-card"><div class="stat-icon" style="background:#d1fae5"><i class="bi bi-check-circle-fill" style="color:#065f46"></i></div><div><div class="stat-value text-success">{{ summary.pass }}</div><div class="stat-label">Passing</div></div></div></div>
      <div class="col-md-4"><div class="stat-card"><div class="stat-icon" style="background:#fef3c7"><i class="bi bi-exclamation-triangle-fill" style="color:#92400e"></i></div><div><div class="stat-value text-warning">{{ summary.warning }}</div><div class="stat-label">Warnings</div></div></div></div>
      <div class="col-md-4"><div class="stat-card"><div class="stat-icon" style="background:#fee2e2"><i class="bi bi-x-circle-fill" style="color:#991b1b"></i></div><div><div class="stat-value text-danger">{{ summary.fail }}</div><div class="stat-label">Failures</div></div></div></div>
    </div>
    <div class="row g-3">
      <div class="col-md-6" v-for="c in checks" :key="c.name">
        <div class="cos-card audit-check-card" :class="c.status">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <h6 class="fw-bold mb-1">{{ c.check }}</h6>
              <span class="badge" :class="c.category==='finance'?'bg-primary':'bg-secondary'">{{ c.category }}</span>
              <span class="badge ms-1" :class="c.severity==='critical'?'bg-danger':c.severity==='warning'?'bg-warning text-dark':'bg-info'">{{ c.severity }}</span>
            </div>
            <span class="audit-status-icon"><i :class="`bi ${c.status==='pass'?'bi-check-circle-fill text-success':c.status==='fail'?'bi-x-circle-fill text-danger':'bi-exclamation-triangle-fill text-warning'}`" style="font-size:22px"></i></span>
          </div>
          <p class="text-muted small mb-2">{{ c.summary }}</p>
          <div class="d-flex justify-content-between align-items-center">
            <span class="text-muted" style="font-size:11px">{{ c.affected_count > 0 ? `${c.affected_count} affected` : "" }} · {{ fmt(c.run_at) }}</span>
            <button v-if="!c.resolved && c.status!=='pass'" class="btn btn-xs btn-outline-success" @click="resolve(c)">Mark Resolved</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from "vue"
import dayjs from "dayjs"
import { auditApi } from "@/api"
const checks = ref([]); const summary = ref(null); const running = ref(false)
const fmt = d => d ? dayjs(d).format("DD MMM HH:mm") : "Never run"
async function load() { const { data } = await auditApi.dashboard(); checks.value = data.checks || []; summary.value = data.summary }
async function runAll() { running.value = true; try { await auditApi.runAll(); await load() } finally { running.value = false } }
async function resolve(c) { const reports = await auditApi.getReports({ check_name: c.check }); const r = (reports.data.results || reports.data)[0]; if (r) { await auditApi.resolveReport(r.id); load() } }
onMounted(load)
</script>
<style scoped>.audit-check-card.fail{border-left:3px solid var(--cos-danger)}.audit-check-card.warning{border-left:3px solid var(--cos-warning)}.audit-check-card.pass{border-left:3px solid var(--cos-success)}.btn-xs{padding:2px 7px;font-size:11px}</style>