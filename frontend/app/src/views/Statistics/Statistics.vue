<template>
  <WorkspaceShell
    title="Statistics Dashboard"
    subtitle="Overview of your geospatial analyses activity."
  >
    <section class="space-y-6">
      <p v-if="errorMessage" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <!-- Filters -->
      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Date</span>
            <select v-model="filters.range" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option value="all">All time</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last month</option>
              <option value="365d">Last year</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Project</span>
            <select v-model="filters.projectId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All projects</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Dataset</span>
            <select v-model="filters.datasetId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All datasets</option>
              <option v-for="d in datasets" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Indicator</span>
            <select v-model="filters.indicatorId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All indicators</option>
              <option v-for="i in indicators" :key="i.id" :value="i.id">{{ i.name }}</option>
            </select>
          </label>
        </div>
      </div>

      <!-- KPI cards -->
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article v-for="card in kpiCards" :key="card.label" class="rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">{{ card.label }}</p>
          <h3 class="mt-2 text-2xl font-black tracking-tight text-slate-900">{{ card.value }}</h3>
        </article>
      </div>

      <!-- Charts row 1 -->
      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Analysis by Indicator</h2>
          <p class="mt-1 text-sm text-slate-500">Number of analyses run per indicator.</p>
          <div class="mt-4 h-64">
            <Bar v-if="indicatorChartData" :data="indicatorChartData" :options="barOptions" />
            <p v-else class="pt-16 text-center text-sm text-slate-400">No data yet.</p>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Analysis Status</h2>
          <p class="mt-1 text-sm text-slate-500">Completed vs running vs failed.</p>
          <div class="mt-4 flex h-64 items-center justify-center">
            <Pie v-if="statusChartData" :data="statusChartData" :options="pieOptions" />
            <p v-else class="text-sm text-slate-400">No data yet.</p>
          </div>
        </div>
      </div>

      <!-- Charts row 2 -->
      <div class="grid gap-6 xl:grid-cols-2">
        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Dataset Usage</h2>
          <p class="mt-1 text-sm text-slate-500">Which datasets get analyzed the most.</p>
          <div class="mt-4 flex h-64 items-center justify-center">
            <Doughnut v-if="datasetChartData" :data="datasetChartData" :options="pieOptions" />
            <p v-else class="text-sm text-slate-400">No data yet.</p>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Monthly Activity</h2>
          <p class="mt-1 text-sm text-slate-500">Analyses run per month.</p>
          <div class="mt-4 h-64">
            <Line v-if="monthlyChartData" :data="monthlyChartData" :options="lineOptions" />
            <p v-else class="pt-16 text-center text-sm text-slate-400">No data yet.</p>
          </div>
        </div>
      </div>

      <!-- Project activity + Recent analyses -->
      <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Project Activity</h2>
          <p class="mt-1 text-sm text-slate-500">Analyses run per project.</p>
          <div class="mt-4 h-64">
            <Bar v-if="projectChartData" :data="projectChartData" :options="horizontalBarOptions" />
            <p v-else class="pt-16 text-center text-sm text-slate-400">No data yet.</p>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Recent Analyses</h2>
          <p class="mt-1 text-sm text-slate-500">Latest activity across all projects.</p>
          <div v-if="recentAnalyses.length === 0" class="mt-6 text-center text-sm text-slate-400">No analyses yet.</div>
          <div v-else class="mt-4 space-y-2">
            <button
              v-for="a in recentAnalyses"
              :key="a.id"
              class="flex w-full items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-3 text-left text-sm transition hover:border-slate-200 hover:bg-slate-50"
              @click="router.push(`/projects/${a.project_id}/analysis/${a.id}`)"
            >
              <span class="font-semibold text-slate-800">{{ a.name }}</span>
              <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(a.status)">{{ a.status }}</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import {
  Chart,
  BarElement,
  BarController,
  ArcElement,
  PieController,
  DoughnutController,
  LineElement,
  LineController,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import api from '@/services/api'

Chart.register(BarElement, BarController, ArcElement, PieController, DoughnutController, LineElement, LineController, PointElement, CategoryScale, LinearScale, Tooltip, Legend)

const router = useRouter()

const PALETTE = ['#6366f1', '#22c55e', '#0ea5e9', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e']

const projects = ref([])
const datasets = ref([])
const indicators = ref([])
const analyses = ref([])

const overview = ref(null)
const statusBreakdown = ref([])
const indicatorUsage = ref([])
const datasetUsage = ref([])
const monthlyActivity = ref([])
const projectActivity = ref([])

const errorMessage = ref('')

const filters = ref({ range: 'all', projectId: null, datasetId: null, indicatorId: null })

function dateFromForRange(range) {
  if (range === 'all') return null
  const days = { '7d': 7, '30d': 30, '365d': 365 }[range]
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 10)
}

function buildParams() {
  const params = {}
  const dateFrom = dateFromForRange(filters.value.range)
  if (dateFrom) params.date_from = dateFrom
  if (filters.value.projectId) params.project_id = filters.value.projectId
  if (filters.value.datasetId) params.dataset_id = filters.value.datasetId
  if (filters.value.indicatorId) params.indicator_id = filters.value.indicatorId
  return params
}

async function fetchStatistics() {
  errorMessage.value = ''
  try {
    const params = buildParams()
    const [overviewRes, statusRes, indicatorsRes, datasetsRes, monthlyRes, projectsRes] = await Promise.all([
      api.get('statistics/overview', { params }),
      api.get('statistics/status', { params }),
      api.get('statistics/indicators', { params }),
      api.get('statistics/datasets', { params }),
      api.get('statistics/monthly', { params }),
      api.get('statistics/projects', { params }),
    ])
    overview.value = overviewRes.data
    statusBreakdown.value = statusRes.data
    indicatorUsage.value = indicatorsRes.data
    datasetUsage.value = datasetsRes.data
    monthlyActivity.value = monthlyRes.data
    projectActivity.value = projectsRes.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load statistics.'
  }
}

async function loadFilterOptions() {
  try {
    const [projectsRes, datasetsRes, indicatorsRes, analysesRes] = await Promise.all([
      api.get('projects'),
      api.get('datasets'),
      api.get('indicators'),
      api.get('analyses'),
    ])
    projects.value = projectsRes.data
    datasets.value = datasetsRes.data
    indicators.value = indicatorsRes.data
    analyses.value = analysesRes.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load filter options.'
  }
}

onMounted(async () => {
  await loadFilterOptions()
  await fetchStatistics()
})

watch(filters, fetchStatistics, { deep: true })

const kpiCards = computed(() => {
  const o = overview.value
  if (!o) return []
  return [
    { label: 'Total Projects', value: o.projects },
    { label: 'Total Analyses', value: o.analyses },
    { label: 'Completed', value: o.completed },
    { label: 'Running', value: o.running },
    { label: 'Failed', value: o.failed },
    { label: 'Exports', value: o.exports },
    { label: 'Total Area Analyzed', value: `${o.total_area_ha} ha` },
    { label: 'Avg. Processing Time', value: o.avg_processing_time != null ? `${o.avg_processing_time}s` : '—' },
  ]
})

const recentAnalyses = computed(() =>
  [...analyses.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 6)
)

const indicatorChartData = computed(() => {
  if (!indicatorUsage.value.length) return null
  return {
    labels: indicatorUsage.value.map((i) => i.indicator),
    datasets: [{ label: 'Analyses', data: indicatorUsage.value.map((i) => i.count), backgroundColor: '#6366f1' }],
  }
})

const statusChartData = computed(() => {
  if (!statusBreakdown.value.length) return null
  const colors = { Completed: '#22c55e', Running: '#f59e0b', Failed: '#ef4444', Pending: '#94a3b8' }
  return {
    labels: statusBreakdown.value.map((s) => s.status),
    datasets: [{ data: statusBreakdown.value.map((s) => s.count), backgroundColor: statusBreakdown.value.map((s) => colors[s.status] || '#94a3b8') }],
  }
})

const datasetChartData = computed(() => {
  if (!datasetUsage.value.length) return null
  return {
    labels: datasetUsage.value.map((d) => d.dataset),
    datasets: [{ data: datasetUsage.value.map((d) => d.count), backgroundColor: PALETTE }],
  }
})

const monthlyChartData = computed(() => {
  if (!monthlyActivity.value.length) return null
  return {
    labels: monthlyActivity.value.map((m) => m.month),
    datasets: [{ label: 'Analyses', data: monthlyActivity.value.map((m) => m.count), borderColor: '#6366f1', backgroundColor: '#6366f1', tension: 0.3 }],
  }
})

const projectChartData = computed(() => {
  if (!projectActivity.value.length) return null
  return {
    labels: projectActivity.value.map((p) => p.project),
    datasets: [{ label: 'Analyses', data: projectActivity.value.map((p) => p.count), backgroundColor: '#6366f1' }],
  }
})

const barOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
const horizontalBarOptions = { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
const lineOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
const pieOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}
</script>
