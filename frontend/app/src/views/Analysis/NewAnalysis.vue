<template>
  <WorkspaceShell title="New Analysis" subtitle="Run a new geospatial analysis on Google Earth Engine.">
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.back()">
        Cancel
      </button>
    </template>

    <section class="mx-auto max-w-3xl space-y-6">
      <p v-if="loadError" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ loadError }}</p>

      <!-- Project / Dataset -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <div class="grid gap-4 sm:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Project</span>
            <select v-model="form.projectId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Dataset</span>
            <select v-model="form.datasetId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="d in datasets" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </label>
        </div>
      </div>

      <!-- Zone d'étude -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-bold text-slate-900">Area Of Interest (AOI)</h2>
          <span v-if="form.area" class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">{{ form.area }} ha</span>
        </div>

        <div class="mb-3 flex flex-wrap gap-1 rounded-xl bg-slate-50 p-1">
          <button v-for="tab in aoiTabs" :key="tab.id" type="button" class="flex-1 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold transition" :class="aoiTab === tab.id ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'" @click="aoiTab = tab.id">
            {{ tab.label }}
          </button>
          <button type="button" class="rounded-lg px-3 py-1.5 text-xs font-semibold text-rose-500 transition hover:bg-rose-50" @click="clearAoi()">
            Clear
          </button>
        </div>

        <!-- Administrative -->
        <div v-if="aoiTab === 'admin'" class="space-y-3">
          <div class="grid gap-3 sm:grid-cols-2">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Country</span>
              <select v-model="adminCountry" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" @change="onCountryChange">
                <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
              </select>
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Region (optional)</span>
              <select v-model="adminRegion" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
                <option :value="null">Whole country</option>
                <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
              </select>
            </label>
          </div>
          <button type="button" class="w-full rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-50" :disabled="isLoadingAdminGeometry" @click="applyAdminGeometry()">
            {{ isLoadingAdminGeometry ? 'Loading boundary…' : 'Use this boundary' }}
          </button>
        </div>

        <!-- Draw -->
        <div v-show="aoiTab === 'draw'" class="h-[320px] overflow-hidden rounded-2xl border border-slate-200">
          <AoiDrawer :key="drawerKey" @change="onAoiDrawn" />
        </div>

        <!-- GeoJSON -->
        <div v-if="aoiTab === 'geojson'" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center">
          <input ref="geojsonInput" type="file" accept=".json,.geojson" class="hidden" @change="handleGeojsonUpload" />
          <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50" @click="geojsonInput.click()">
            Choose .geojson file
          </button>
        </div>

        <!-- Shapefile -->
        <div v-if="aoiTab === 'shapefile'" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center">
          <input ref="shapefileInput" type="file" accept=".zip" class="hidden" @change="handleShapefileUpload" />
          <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50" @click="shapefileInput.click()">
            Choose .zip file
          </button>
          <p class="mt-2 text-[11px] text-slate-400">Zip containing .shp, .shx, .dbf (and .prj)</p>
          <p v-if="isUploadingAoi" class="mt-2 text-xs font-semibold text-[#6366f1]">Parsing shapefile…</p>
        </div>

        <!-- KML -->
        <div v-if="aoiTab === 'kml'" class="rounded-2xl border border-dashed border-slate-200 bg-slate-50/70 p-6 text-center">
          <input ref="kmlInput" type="file" accept=".kml" class="hidden" @change="handleKmlUpload" />
          <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50" @click="kmlInput.click()">
            Choose .kml file
          </button>
          <p v-if="isUploadingAoi" class="mt-2 text-xs font-semibold text-[#6366f1]">Parsing KML…</p>
        </div>

        <div v-if="aoiPreviewPolygon.length && aoiTab !== 'draw'" class="mt-3 h-[220px] overflow-hidden rounded-2xl border border-slate-200">
          <ProjectAoiMap :center="aoiPreviewCenter" :polygon="aoiPreviewPolygon" />
        </div>
      </div>

      <!-- Période -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">Date Range</h2>
        <div class="mt-3 flex flex-wrap gap-1 rounded-xl bg-slate-50 p-1">
          <button v-for="tab in periodTabs" :key="tab.id" type="button" class="flex-1 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold transition" :class="periodTab === tab.id ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'" @click="periodTab = tab.id">
            {{ tab.label }}
          </button>
        </div>

        <div v-if="periodTab === 'year'" class="mt-4">
          <span class="mb-1.5 block text-xs font-semibold text-slate-700">Year</span>
          <select v-model.number="period.year" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1] sm:w-40">
            <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>

        <div v-else-if="periodTab === 'season'" class="mt-4 grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Year</span>
            <select v-model.number="period.year" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Season</span>
            <select v-model="period.season" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="s in seasons" :key="s" :value="s">{{ s }}</option>
            </select>
          </label>
        </div>

        <div v-else-if="periodTab === 'month'" class="mt-4 grid gap-3 sm:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Year</span>
            <select v-model.number="period.year" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Month</span>
            <select v-model.number="period.month" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="(m, i) in monthNames" :key="m" :value="i + 1">{{ m }}</option>
            </select>
          </label>
        </div>

        <div v-else-if="periodTab === 'compare'" class="mt-4 grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl border border-slate-100 bg-slate-50/70 p-3">
            <p class="mb-2 text-xs font-black uppercase tracking-[0.2em] text-slate-400">Period A</p>
            <input v-model="period.compareA.start" type="date" class="mb-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
            <input v-model="period.compareA.end" type="date" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </div>
          <div class="rounded-2xl border border-slate-100 bg-slate-50/70 p-3">
            <p class="mb-2 text-xs font-black uppercase tracking-[0.2em] text-slate-400">Period B</p>
            <input v-model="period.compareB.start" type="date" class="mb-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
            <input v-model="period.compareB.end" type="date" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </div>
        </div>

        <p class="mt-3 text-xs text-slate-500">{{ periodTab === 'compare' ? `${period.compareA.start} → ${period.compareA.end}  vs  ${period.compareB.start} → ${period.compareB.end}` : `${computedDateRange.start} → ${computedDateRange.end}` }}</p>

        <h2 class="mt-5 text-lg font-bold text-slate-900">Resolution</h2>
        <select v-model.number="form.resolution" class="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1] sm:w-48">
          <option :value="10">10 m</option>
          <option :value="30">30 m</option>
          <option :value="250">250 m</option>
        </select>
      </div>

      <!-- Catalogue d'indicateurs -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">Indicator</h2>
        <div class="mt-3 space-y-4">
          <div v-for="group in indicatorsByCategory" :key="group.category">
            <p class="mb-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-400">{{ group.category }}</p>
            <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              <button
                v-for="indicator in group.items"
                :key="indicator.id"
                type="button"
                class="rounded-2xl border p-3 text-left transition"
                :class="indicator.id === form.indicatorId ? 'border-[#6366f1] bg-[#eef2ff]' : 'border-slate-200 hover:border-slate-300'"
                @click="form.indicatorId = indicator.id"
              >
                <p class="text-sm font-bold" :class="indicator.id === form.indicatorId ? 'text-[#4f46e5]' : 'text-slate-800'">{{ indicator.name }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ indicator.description }}</p>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Parameters -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">Parameters</h2>

        <div v-if="parameterMode === 'cloud'" class="mt-3">
          <span class="mb-1.5 block text-xs font-semibold text-slate-700">Cloud Cover (max %)</span>
          <input v-model.number="form.cloudPercentage" type="number" min="0" max="100" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1] sm:w-40" />
        </div>
        <p v-else class="mt-2 text-sm text-slate-500">No additional parameters for this indicator.</p>
      </div>

      <!-- Summary -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">Estimated Output</h2>
        <div class="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <p><span class="block text-xs font-semibold text-slate-500">Project</span>{{ selectedProjectName || '—' }}</p>
          <p><span class="block text-xs font-semibold text-slate-500">Dataset</span>{{ selectedDatasetName || '—' }}</p>
          <p><span class="block text-xs font-semibold text-slate-500">Indicator</span>{{ selectedIndicatorName || '—' }}</p>
          <p><span class="block text-xs font-semibold text-slate-500">Area</span>{{ form.area ? `${form.area} ha` : '—' }}</p>
          <p><span class="block text-xs font-semibold text-slate-500">Resolution</span>{{ form.resolution }} m</p>
        </div>
      </div>

      <p v-if="runError" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ runError }}</p>

      <div v-if="isRunning" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <p class="text-sm font-semibold text-slate-700">Running Analysis… <span class="text-slate-400">Google Earth Engine</span></p>
        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
          <div class="h-2 animate-pulse rounded-full bg-[#6366f1]" style="width: 70%"></div>
        </div>
      </div>

      <div class="flex justify-end gap-3">
        <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="router.back()">Cancel</button>
        <button
          class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
          :disabled="isRunning || !canRun"
          @click="runAnalysis()"
        >
          {{ isRunning ? 'Running…' : periodTab === 'compare' ? 'Run Comparison' : 'Run Analysis' }}
        </button>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import AoiDrawer from '@/components/Map/AoiDrawer.vue'
import ProjectAoiMap from '@/components/Map/ProjectAoiMap.vue'
import { polygonAreaHectares } from '@/utils/geo'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const projects = ref([])
const datasets = ref([])
const indicators = ref([])
const loadError = ref('')

const aoiTabs = [
  { id: 'admin', label: 'Administrative' },
  { id: 'draw', label: 'Draw' },
  { id: 'geojson', label: 'GeoJSON' },
  { id: 'shapefile', label: 'Shapefile' },
  { id: 'kml', label: 'KML' },
]
const aoiTab = ref('draw')
const drawerKey = ref(0)
const geojsonInput = ref(null)
const shapefileInput = ref(null)
const kmlInput = ref(null)
const isUploadingAoi = ref(false)

const countries = ref([])
const regions = ref([])
const adminCountry = ref(null)
const adminRegion = ref(null)
const isLoadingAdminGeometry = ref(false)

const periodTabs = [
  { id: 'year', label: 'Year' },
  { id: 'season', label: 'Season' },
  { id: 'month', label: 'Month' },
  { id: 'compare', label: 'Compare 2 Periods' },
]
const periodTab = ref('year')
const seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const currentYear = new Date().getFullYear()
const yearOptions = Array.from({ length: 15 }, (_, i) => currentYear - i)

const period = ref({
  year: currentYear,
  season: 'Winter',
  month: 1,
  compareA: { start: '2015-01-01', end: '2015-12-31' },
  compareB: { start: '2024-01-01', end: '2024-12-31' },
})

const isRunning = ref(false)
const runError = ref('')

const form = ref({
  projectId: null,
  datasetId: null,
  indicatorId: null,
  resolution: 10,
  cloudPercentage: 20,
  geometry: null,
  area: null,
})

async function loadOptions() {
  loadError.value = ''
  try {
    const [projectsRes, datasetsRes, indicatorsRes, countriesRes] = await Promise.all([
      api.get('projects'),
      api.get('datasets'),
      api.get('indicators'),
      api.get('regions/countries'),
    ])
    projects.value = projectsRes.data
    datasets.value = datasetsRes.data
    indicators.value = indicatorsRes.data
    countries.value = countriesRes.data
    adminCountry.value = countries.value[0] ?? null

    const preselectProjectId = route.query.project ? Number(route.query.project) : null
    form.value.projectId = preselectProjectId && projects.value.some((p) => p.id === preselectProjectId)
      ? preselectProjectId
      : projects.value[0]?.id ?? null

    const preselectIndicatorId = route.query.indicator ? Number(route.query.indicator) : null
    const preselectIndicator = preselectIndicatorId ? indicators.value.find((i) => i.id === preselectIndicatorId) : null

    if (preselectIndicator && GENERIC_BUILDER_INDICATORS.includes(preselectIndicator.name)) {
      form.value.datasetId = datasets.value.find((d) => GENERIC_BUILDER_PROVIDERS.includes(d.provider))?.id ?? datasets.value[0]?.id ?? null
    } else if (preselectIndicator && DATASET_LOCKED_PROVIDERS[preselectIndicator.name]) {
      const requiredProvider = DATASET_LOCKED_PROVIDERS[preselectIndicator.name]
      form.value.datasetId = datasets.value.find((d) => d.provider === requiredProvider)?.id ?? datasets.value[0]?.id ?? null
    } else {
      form.value.datasetId = datasets.value[0]?.id ?? null
    }

    form.value.indicatorId = preselectIndicator && !UNSUPPORTED_INDICATORS.includes(preselectIndicator.name)
      ? preselectIndicatorId
      : indicatorsByCategory.value[0]?.items[0]?.id ?? null

    if (adminCountry.value) onCountryChange()
  } catch (error) {
    loadError.value = error.response?.data?.detail || 'Unable to load projects, datasets, or indicators.'
  }
}

onMounted(loadOptions)

async function onCountryChange() {
  adminRegion.value = null
  regions.value = []
  if (!adminCountry.value) return
  try {
    const { data } = await api.get(`regions/${adminCountry.value}/regions`)
    regions.value = data
  } catch (error) {
    runError.value = error.response?.data?.detail || 'Unable to load regions for this country.'
  }
}

async function applyAdminGeometry() {
  isLoadingAdminGeometry.value = true
  runError.value = ''
  try {
    const { data } = await api.get('regions/geometry', { params: { country: adminCountry.value, region: adminRegion.value } })
    form.value.geometry = data.geometry
    form.value.area = Math.round(data.area * 100) / 100
  } catch (error) {
    runError.value = error.response?.data?.detail || 'Unable to load this boundary.'
  } finally {
    isLoadingAdminGeometry.value = false
  }
}

const selectedProjectName = computed(() => projects.value.find((p) => p.id === form.value.projectId)?.name)
const selectedDataset = computed(() => datasets.value.find((d) => d.id === form.value.datasetId))
const selectedDatasetName = computed(() => selectedDataset.value?.name)
const selectedIndicator = computed(() => indicators.value.find((i) => i.id === form.value.indicatorId))
const selectedIndicatorName = computed(() => selectedIndicator.value?.name)

// Mirrors the real compute compatibility in backend/app/core/gee_compute.py:
// - these 4 only have a band-math builder for Sentinel-2 / Landsat-8
// - LST and Precipitation are hardcoded to one specific provider each
// - Vulnerability/Exposure/Sensitivity have no handler implemented at all
// - every other indicator (Land Cover, Population, Soil Moisture, Drought…) uses
//   its own fixed GEE source internally and ignores the selected dataset entirely
const GENERIC_BUILDER_INDICATORS = ['NDVI', 'EVI', 'SAVI', 'NDWI']
const GENERIC_BUILDER_PROVIDERS = ['Sentinel-2', 'Landsat-8']
const DATASET_LOCKED_PROVIDERS = {
  'Land Surface Temperature (Température de surface)': 'MODIS',
  'Precipitation (Précipitations)': 'CHIRPS',
}
const UNSUPPORTED_INDICATORS = ['Vulnerability (Vulnérabilité)', 'Exposure (Exposition)', 'Sensitivity (Sensibilité)']

function isIndicatorRunnable(indicator, dataset) {
  if (UNSUPPORTED_INDICATORS.includes(indicator.name)) return false
  if (GENERIC_BUILDER_INDICATORS.includes(indicator.name)) {
    return Boolean(dataset && GENERIC_BUILDER_PROVIDERS.includes(dataset.provider))
  }
  const lockedProvider = DATASET_LOCKED_PROVIDERS[indicator.name]
  if (lockedProvider) {
    return Boolean(dataset && dataset.provider === lockedProvider)
  }
  return true
}

const indicatorsByCategory = computed(() => {
  const groups = new Map()
  for (const indicator of indicators.value) {
    if (!isIndicatorRunnable(indicator, selectedDataset.value)) continue
    if (!groups.has(indicator.category)) groups.set(indicator.category, [])
    groups.get(indicator.category).push(indicator)
  }
  return Array.from(groups.entries()).map(([category, items]) => ({ category, items }))
})

// keep the selected indicator valid whenever the dataset changes
watch(selectedDataset, (dataset) => {
  if (selectedIndicator.value && !isIndicatorRunnable(selectedIndicator.value, dataset)) {
    form.value.indicatorId = indicatorsByCategory.value[0]?.items[0]?.id ?? null
  }
})

const parameterMode = computed(() => {
  const name = selectedIndicatorName.value
  if (['NDVI', 'EVI', 'SAVI', 'NDWI'].includes(name)) return 'cloud'
  return null
})

function pad(n) {
  return String(n).padStart(2, '0')
}

const computedDateRange = computed(() => {
  if (periodTab.value === 'year') {
    return { start: `${period.value.year}-01-01`, end: `${period.value.year}-12-31` }
  }
  if (periodTab.value === 'season') {
    const y = period.value.year
    const ranges = {
      Winter: [`${y}-12-01`, `${y + 1}-02-28`],
      Spring: [`${y}-03-01`, `${y}-05-31`],
      Summer: [`${y}-06-01`, `${y}-08-31`],
      Autumn: [`${y}-09-01`, `${y}-11-30`],
    }
    const [start, end] = ranges[period.value.season]
    return { start, end }
  }
  if (periodTab.value === 'month') {
    const y = period.value.year
    const m = period.value.month
    const lastDay = new Date(y, m, 0).getDate()
    return { start: `${y}-${pad(m)}-01`, end: `${y}-${pad(m)}-${pad(lastDay)}` }
  }
  return { start: period.value.compareA.start, end: period.value.compareA.end }
})

const canRun = computed(() => Boolean(form.value.projectId && form.value.datasetId && form.value.indicatorId && form.value.geometry))

const aoiPreviewCenter = computed(() => {
  if (!aoiPreviewPolygon.value.length) return [31.5, -6.5]
  const lats = aoiPreviewPolygon.value.map((c) => c[0])
  const lngs = aoiPreviewPolygon.value.map((c) => c[1])
  return [(Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lngs) + Math.max(...lngs)) / 2]
})

const aoiPreviewPolygon = computed(() => {
  if (!form.value.geometry) return []
  const ring = form.value.geometry.type === 'Polygon' ? form.value.geometry.coordinates[0] : form.value.geometry.coordinates[0][0]
  return ring.map(([lng, lat]) => [lat, lng])
})

function onAoiDrawn({ geometry, areaHa }) {
  form.value.geometry = geometry
  form.value.area = geometry ? Math.round(areaHa * 100) / 100 : null
}

function clearAoi() {
  form.value.geometry = null
  form.value.area = null
  drawerKey.value += 1
}

async function handleGeojsonUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  try {
    const text = await file.text()
    const parsed = JSON.parse(text)
    const geometry =
      parsed.type === 'FeatureCollection'
        ? parsed.features?.[0]?.geometry
        : parsed.type === 'Feature'
          ? parsed.geometry
          : parsed

    if (!geometry || !['Polygon', 'MultiPolygon'].includes(geometry.type)) {
      runError.value = 'This GeoJSON file must contain a Polygon or MultiPolygon geometry.'
      return
    }

    form.value.geometry = geometry
    form.value.area = Math.round(polygonAreaHectares(geometry) * 100) / 100
    runError.value = ''
  } catch (error) {
    runError.value = 'Invalid GeoJSON file.'
  } finally {
    event.target.value = ''
  }
}

async function handleShapefileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  isUploadingAoi.value = true
  try {
    const payload = new FormData()
    payload.append('file', file)
    const { data } = await api.post('projects/aoi/shapefile', payload, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.geometry = data.geometry
    form.value.area = Math.round(data.area * 100) / 100
  } catch (error) {
    runError.value = error.response?.data?.detail || 'Unable to parse the shapefile.'
  } finally {
    isUploadingAoi.value = false
    event.target.value = ''
  }
}

async function handleKmlUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  isUploadingAoi.value = true
  try {
    const payload = new FormData()
    payload.append('file', file)
    const { data } = await api.post('projects/aoi/kml', payload, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.geometry = data.geometry
    form.value.area = Math.round(data.area * 100) / 100
  } catch (error) {
    runError.value = error.response?.data?.detail || 'Unable to parse the KML file.'
  } finally {
    isUploadingAoi.value = false
    event.target.value = ''
  }
}

async function runAnalysis() {
  runError.value = ''
  isRunning.value = true
  try {
    if (periodTab.value === 'compare') {
      const base = {
        project_id: form.value.projectId,
        dataset_id: form.value.datasetId,
        indicator_id: form.value.indicatorId,
        resolution: form.value.resolution,
        cloud_percentage: parameterMode.value === 'cloud' ? form.value.cloudPercentage : null,
        aoi: form.value.geometry,
      }
      const [resA, resB] = await Promise.all([
        api.post('analyses', { ...base, start_date: period.value.compareA.start, end_date: period.value.compareA.end }),
        api.post('analyses', { ...base, start_date: period.value.compareB.start, end_date: period.value.compareB.end }),
      ])
      router.push(`/projects/${form.value.projectId}/analysis/compare?a=${resA.data.id}&b=${resB.data.id}`)
    } else {
      const { data } = await api.post('analyses', {
        project_id: form.value.projectId,
        dataset_id: form.value.datasetId,
        indicator_id: form.value.indicatorId,
        start_date: computedDateRange.value.start,
        end_date: computedDateRange.value.end,
        resolution: form.value.resolution,
        cloud_percentage: parameterMode.value === 'cloud' ? form.value.cloudPercentage : null,
        aoi: form.value.geometry,
      })
      router.push(`/projects/${form.value.projectId}/analysis/${data.id}`)
    }
  } catch (error) {
    runError.value = error.response?.data?.detail || 'Unable to run the analysis.'
  } finally {
    isRunning.value = false
  }
}
</script>
