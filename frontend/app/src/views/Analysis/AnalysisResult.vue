<template>
  <WorkspaceShell :title="analysis ? analysis.name : 'Analysis Result'" subtitle="Result of the geospatial analysis run on Google Earth Engine.">
    <template #actions>
      <button
        v-if="analysis"
        class="rounded-xl border px-4 py-2 text-sm font-semibold shadow-sm transition disabled:opacity-60"
        :class="isFavorited ? 'border-amber-200 bg-amber-50 text-amber-700 hover:bg-amber-100' : 'border-slate-100 bg-white text-slate-700 hover:border-slate-200 hover:bg-slate-50'"
        :disabled="isTogglingFavorite"
        @click="toggleFavorite()"
      >
        {{ isFavorited ? '★ Favorited' : '☆ Save' }}
      </button>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push(`/projects/${route.params.projectId}`)">
        ← Back to Project
      </button>
    </template>

    <section class="mx-auto max-w-3xl space-y-6">
      <p v-if="errorMessage" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading result…
      </div>

      <template v-else-if="analysis">
        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-900">{{ analysis.name }}</h2>
            <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusClass(analysis.status)">{{ analysis.status }}</span>
          </div>
          <div class="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <p><span class="block text-xs font-semibold text-slate-500">Resolution</span>{{ analysis.scale }} m</p>
            <p><span class="block text-xs font-semibold text-slate-500">Cloud Cover</span>{{ analysis.cloud_percentage ?? '—' }}%</p>
            <p><span class="block text-xs font-semibold text-slate-500">Processing Time</span>{{ analysis.processing_time ? `${analysis.processing_time.toFixed(2)}s` : '—' }}</p>
            <p><span class="block text-xs font-semibold text-slate-500">Start Date</span>{{ formatDate(analysis.start_date) }}</p>
            <p><span class="block text-xs font-semibold text-slate-500">End Date</span>{{ formatDate(analysis.end_date) }}</p>
          </div>
        </div>

        <p v-if="analysis.status === 'Failed'" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">
          {{ analysis.error_message || 'This analysis failed to compute.' }}
        </p>

        <template v-else>
          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Statistics</h2>
            <p class="mt-1 text-sm text-slate-500">Computed by Google Earth Engine over the AOI.</p>
            <div v-if="analysis.stats" class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div v-for="stat in statCards" :key="stat.label" class="rounded-2xl border border-slate-100 bg-slate-50/70 p-3 text-center">
                <p class="text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">{{ stat.label }}</p>
                <p class="mt-1 text-lg font-black tabular-nums text-slate-900">{{ stat.value }}</p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-slate-500">No statistics available.</p>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Result Map</h2>
            <ProjectAoiMap :center="mapCenter" :polygon="mapPolygon" :overlay-url="analysis.tile_url" class="mt-3 h-[360px] rounded-[20px] overflow-hidden" />
          </div>

          <div v-if="histogramData" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Histogram</h2>
            <p class="mt-1 text-sm text-slate-500">Pixel value distribution over the AOI.</p>
            <div class="mt-4 h-56">
              <Bar :data="histogramData" :options="histogramOptions" />
            </div>
          </div>

          <div v-if="timeseriesData" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Time Series</h2>
            <p class="mt-1 text-sm text-slate-500">Mean value over sub-periods within the date range.</p>
            <div class="mt-4 h-56">
              <Line :data="timeseriesData" :options="timeseriesOptions" />
            </div>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Export Results</h2>
                <p class="mt-1 text-sm text-slate-500">Generates a file and adds it to the Export Center.</p>
              </div>
              <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="showExportModal = true">
                Export Results
              </button>
            </div>

            <p v-if="exportsError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ exportsError }}</p>

            <div v-if="exports.length" class="mt-4 space-y-2">
              <div
                v-for="exp in exports"
                :key="exp.id"
                class="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-3 text-sm"
              >
                <div>
                  <p class="font-semibold text-slate-800">{{ exp.file_name }}</p>
                  <p class="text-xs text-slate-500">{{ formatSize(exp.file_size) }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="exportStatusClass(exp.status)">{{ exp.status }}</span>
                  <button
                    v-if="exp.status === 'Completed'"
                    class="rounded-lg border border-slate-200 px-2.5 py-1 text-xs font-semibold text-slate-600 transition hover:bg-white"
                    @click="downloadExport(exp)"
                  >
                    Download
                  </button>
                </div>
              </div>
            </div>

            <router-link :to="`/exports?analysis=${analysis.id}`" class="mt-4 inline-block text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5]">
              View all in Export Center →
            </router-link>
          </div>

          <div v-if="showExportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="showExportModal = false">
            <div class="w-full max-w-sm rounded-[28px] bg-white p-6 shadow-xl">
              <h3 class="text-lg font-bold text-slate-900">Choose Format</h3>
              <div class="mt-4 space-y-2">
                <label
                  v-for="format in formats"
                  :key="format"
                  class="flex cursor-pointer items-center gap-3 rounded-2xl border p-3 transition"
                  :class="selectedFormat === format ? 'border-[#6366f1] bg-[#eef2ff]' : 'border-slate-200 hover:border-slate-300'"
                >
                  <input type="radio" :value="format" v-model="selectedFormat" class="accent-[#6366f1]" />
                  <span class="text-sm font-semibold text-slate-800">{{ format }}</span>
                </label>
              </div>
              <div class="mt-6 flex justify-end gap-3">
                <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="showExportModal = false">Cancel</button>
                <button
                  class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
                  :disabled="isCreatingExport"
                  @click="createExport()"
                >
                  {{ isCreatingExport ? 'Generating…' : 'Export' }}
                </button>
              </div>
            </div>
          </div>
        </template>
      </template>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bar, Line } from 'vue-chartjs'
import { Chart, BarElement, BarController, LineElement, LineController, PointElement, CategoryScale, LinearScale, Tooltip } from 'chart.js'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import ProjectAoiMap from '@/components/Map/ProjectAoiMap.vue'
import api from '@/services/api'

Chart.register(BarElement, BarController, LineElement, LineController, PointElement, CategoryScale, LinearScale, Tooltip)

const route = useRoute()
const router = useRouter()

const analysis = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const isFavorited = ref(false)
const isTogglingFavorite = ref(false)

async function fetchAnalysis() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get(`analyses/${route.params.analysisId}`)
    analysis.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load this analysis.'
  } finally {
    isLoading.value = false
  }
}

async function fetchFavoriteState() {
  try {
    const { data } = await api.get('favorites')
    isFavorited.value = data.some((f) => f.analysis_id === Number(route.params.analysisId))
  } catch {
    // non-critical — the Save button just won't reflect an initial state
  }
}

async function toggleFavorite() {
  isTogglingFavorite.value = true
  try {
    if (isFavorited.value) {
      await api.delete(`favorites/by-analysis/${route.params.analysisId}`)
      isFavorited.value = false
    } else {
      await api.post('favorites', { analysis_id: Number(route.params.analysisId) })
      isFavorited.value = true
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to update favorite.'
  } finally {
    isTogglingFavorite.value = false
  }
}

onMounted(() => {
  fetchAnalysis()
  fetchFavoriteState()
})

const mapCenter = computed(() => {
  if (!analysis.value?.aoi) return [31.5, -6.5]
  const ring = analysis.value.aoi.type === 'MultiPolygon' ? analysis.value.aoi.coordinates[0][0] : analysis.value.aoi.coordinates[0]
  const lats = ring.map((c) => c[1])
  const lngs = ring.map((c) => c[0])
  return [(Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lngs) + Math.max(...lngs)) / 2]
})

const mapPolygon = computed(() => {
  if (!analysis.value?.aoi) return []
  const ring = analysis.value.aoi.type === 'MultiPolygon' ? analysis.value.aoi.coordinates[0][0] : analysis.value.aoi.coordinates[0]
  return ring.map(([lng, lat]) => [lat, lng])
})

const statCards = computed(() => {
  if (!analysis.value?.stats) return []
  const s = analysis.value.stats
  const fmt = (v) => (typeof v === 'number' ? v.toFixed(3) : '—')
  return [
    { label: 'Min', value: fmt(s.min) },
    { label: 'Max', value: fmt(s.max) },
    { label: 'Mean', value: fmt(s.mean) },
    { label: 'Median', value: fmt(s.median) },
    { label: 'Std Dev', value: fmt(s.stdDev) },
  ]
})

const histogramData = computed(() => {
  const histogram = analysis.value?.stats?.histogram
  if (!histogram || !histogram.length) return null
  return {
    labels: histogram.map((b) => b.bucketStart.toFixed(2)),
    datasets: [{ label: 'Pixel count', data: histogram.map((b) => b.count), backgroundColor: '#6366f1' }],
  }
})

const histogramOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }

const timeseriesData = computed(() => {
  const timeseries = analysis.value?.stats?.timeseries
  if (!timeseries || !timeseries.length) return null
  return {
    labels: timeseries.map((p) => p.date),
    datasets: [{ label: selectedIndicatorLabel.value, data: timeseries.map((p) => p.value), borderColor: '#6366f1', backgroundColor: '#6366f1', tension: 0.3 }],
  }
})

const timeseriesOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }

const selectedIndicatorLabel = computed(() => analysis.value?.name?.split(' · ')[0] || 'Value')

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

const exports = ref([])
const exportsError = ref('')
const showExportModal = ref(false)
const isCreatingExport = ref(false)
const formats = ['GeoTIFF', 'PNG', 'CSV', 'GeoJSON', 'Shapefile']
const selectedFormat = ref('GeoTIFF')

async function fetchExports() {
  try {
    const { data } = await api.get('exports', { params: { analysis_id: route.params.analysisId } })
    exports.value = data
  } catch (error) {
    exportsError.value = error.response?.data?.detail || 'Unable to load exports for this analysis.'
  }
}

async function createExport() {
  isCreatingExport.value = true
  exportsError.value = ''
  try {
    await api.post('exports', { analysis_id: Number(route.params.analysisId), type: selectedFormat.value })
    showExportModal.value = false
    await fetchExports()
  } catch (error) {
    exportsError.value = error.response?.data?.detail || 'Unable to create this export.'
  } finally {
    isCreatingExport.value = false
  }
}

async function downloadExport(exp) {
  try {
    const { data } = await api.get(`exports/download/${exp.id}`, { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = exp.file_name
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    exportsError.value = 'Unable to download this file.'
  }
}

function formatSize(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function exportStatusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Processing') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

onMounted(fetchExports)
</script>
