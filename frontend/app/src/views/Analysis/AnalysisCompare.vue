<template>
  <WorkspaceShell title="Period Comparison" subtitle="Side-by-side comparison of two analysis runs.">
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push(`/projects/${route.params.projectId}`)">
        ← Back to Project
      </button>
    </template>

    <section class="mx-auto max-w-4xl space-y-6">
      <p v-if="errorMessage" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading comparison…
      </div>

      <template v-else-if="analysisA && analysisB">
        <div class="grid gap-6 md:grid-cols-2">
          <div v-for="(a, i) in [analysisA, analysisB]" :key="a.id" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="flex items-center justify-between">
              <p class="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Period {{ i === 0 ? 'A' : 'B' }}</p>
              <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusClass(a.status)">{{ a.status }}</span>
            </div>
            <p class="mt-2 text-sm font-bold text-slate-900">{{ formatDate(a.start_date) }} → {{ formatDate(a.end_date) }}</p>

            <p v-if="a.status === 'Failed'" class="mt-3 text-sm text-rose-600">{{ a.error_message || 'This analysis failed.' }}</p>
            <div v-else-if="a.stats" class="mt-4 grid grid-cols-2 gap-2">
              <div v-for="stat in statCards(a)" :key="stat.label" class="rounded-2xl border border-slate-100 bg-slate-50/70 p-2.5 text-center">
                <p class="text-[9px] font-black uppercase tracking-[0.18em] text-slate-400">{{ stat.label }}</p>
                <p class="mt-1 text-base font-black tabular-nums text-slate-900">{{ stat.value }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="analysisA.status !== 'Failed' && analysisB.status !== 'Failed'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Change</h2>
          <p class="mt-1 text-sm text-slate-500">Difference between Period B and Period A (mean value).</p>
          <div class="mt-4 flex items-center gap-3">
            <span class="text-3xl font-black tabular-nums" :class="delta >= 0 ? 'text-emerald-600' : 'text-rose-600'">
              {{ delta >= 0 ? '+' : '' }}{{ delta.toFixed(3) }}
            </span>
            <span class="text-sm text-slate-500">({{ analysisA.stats.mean.toFixed(3) }} → {{ analysisB.stats.mean.toFixed(3) }})</span>
          </div>
        </div>

        <div class="grid gap-6 md:grid-cols-2">
          <div v-for="(a, i) in [analysisA, analysisB]" :key="`map-${a.id}`" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h3 class="text-sm font-bold text-slate-900">Map — Period {{ i === 0 ? 'A' : 'B' }}</h3>
            <ProjectAoiMap :center="mapCenter(a)" :polygon="mapPolygon(a)" :overlay-url="a.tile_url" class="mt-3 h-[280px] rounded-[20px] overflow-hidden" />
          </div>
        </div>
      </template>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import ProjectAoiMap from '@/components/Map/ProjectAoiMap.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const analysisA = ref(null)
const analysisB = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

async function fetchComparison() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [resA, resB] = await Promise.all([
      api.get(`analyses/${route.query.a}`),
      api.get(`analyses/${route.query.b}`),
    ])
    analysisA.value = resA.data
    analysisB.value = resB.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load this comparison.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchComparison)

const delta = computed(() => {
  if (!analysisA.value?.stats || !analysisB.value?.stats) return 0
  return analysisB.value.stats.mean - analysisA.value.stats.mean
})

function statCards(a) {
  if (!a.stats) return []
  const fmt = (v) => (typeof v === 'number' ? v.toFixed(3) : '—')
  return [
    { label: 'Min', value: fmt(a.stats.min) },
    { label: 'Max', value: fmt(a.stats.max) },
    { label: 'Mean', value: fmt(a.stats.mean) },
    { label: 'Median', value: fmt(a.stats.median) },
  ]
}

function mapCenter(a) {
  if (!a?.aoi) return [31.5, -6.5]
  const ring = a.aoi.type === 'MultiPolygon' ? a.aoi.coordinates[0][0] : a.aoi.coordinates[0]
  const lats = ring.map((c) => c[1])
  const lngs = ring.map((c) => c[0])
  return [(Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lngs) + Math.max(...lngs)) / 2]
}

function mapPolygon(a) {
  if (!a?.aoi) return []
  const ring = a.aoi.type === 'MultiPolygon' ? a.aoi.coordinates[0][0] : a.aoi.coordinates[0]
  return ring.map(([lng, lat]) => [lat, lng])
}

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
