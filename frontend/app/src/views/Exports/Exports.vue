<template>
  <WorkspaceShell
    title="Export Center"
    subtitle="Download and manage every file generated from your analyses."
  >
    <template #actions>
      <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openCreateModal()">
        + Create Export
      </button>
    </template>

    <section class="space-y-6">
      <p v-if="errorMessage" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
        <div class="grid gap-4 sm:grid-cols-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Project</span>
            <select v-model="filterProjectId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All projects</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Analysis</span>
            <select v-model="filterAnalysisId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All analyses</option>
              <option v-for="a in filteredAnalysesForFilter" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">File Type</span>
            <select v-model="filterType" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option :value="null">All types</option>
              <option v-for="f in formats" :key="f" :value="f">{{ f }}</option>
            </select>
          </label>
        </div>
      </div>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading exports…
      </div>

      <div v-else-if="exports.length === 0" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm">
        <div class="mx-auto max-w-sm">
          <div class="text-5xl">📦</div>
          <h3 class="mt-4 text-lg font-bold text-slate-900">No exports yet</h3>
          <p class="mt-2 text-sm text-slate-500">Run an analysis, then export its results — or create one directly here.</p>
        </div>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="exp in exports" :key="exp.id" class="flex flex-col justify-between rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm">
          <div>
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-bold text-slate-900">📄 {{ exp.file_name }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ exp.type }}</p>
              </div>
              <span class="whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(exp.status)">{{ exp.status }}</span>
            </div>

            <div class="mt-4 space-y-1 text-xs text-slate-500">
              <p>{{ formatSize(exp.file_size) }}</p>
              <p>{{ formatDate(exp.created_at) }}</p>
            </div>

            <p v-if="exp.status === 'Failed'" class="mt-3 text-xs font-semibold text-rose-600">{{ exp.error_message }}</p>
          </div>

          <div class="mt-5 flex items-center gap-2 border-t border-slate-100 pt-4">
            <button
              class="flex-1 rounded-xl bg-[#eef2ff] px-3 py-2 text-xs font-semibold text-[#4f46e5] transition hover:bg-[#e0e7ff] disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="exp.status !== 'Completed'"
              @click="downloadExport(exp)"
            >
              Download
            </button>
            <button class="rounded-xl border border-rose-100 px-3 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50" @click="deleteExport(exp)">
              Delete
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Create Export Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="showCreateModal = false">
      <div class="w-full max-w-md rounded-[28px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">Create Export</h3>
        <p class="mt-1 text-sm text-slate-500">Pick a completed analysis and a format.</p>

        <p v-if="createError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ createError }}</p>

        <div class="mt-4 space-y-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Analysis</span>
            <select v-model="createAnalysisId" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option v-for="a in completedAnalyses" :key="a.id" :value="a.id">{{ a.name }}</option>
            </select>
          </label>

          <div>
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Format</span>
            <div class="space-y-2">
              <label
                v-for="format in formats"
                :key="format"
                class="flex cursor-pointer items-center gap-3 rounded-2xl border p-3 transition"
                :class="createFormat === format ? 'border-[#6366f1] bg-[#eef2ff]' : 'border-slate-200 hover:border-slate-300'"
              >
                <input type="radio" :value="format" v-model="createFormat" class="accent-[#6366f1]" />
                <span class="text-sm font-semibold text-slate-800">{{ format }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="showCreateModal = false">Cancel</button>
          <button
            class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
            :disabled="isCreating || !createAnalysisId"
            @click="createExport()"
          >
            {{ isCreating ? 'Generating…' : 'Export' }}
          </button>
        </div>
      </div>
    </div>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import api from '@/services/api'

const route = useRoute()

const formats = ['GeoTIFF', 'PNG', 'CSV', 'GeoJSON', 'Shapefile']

const projects = ref([])
const analyses = ref([])
const exports = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

const filterProjectId = ref(null)
const filterAnalysisId = ref(null)
const filterType = ref(null)

const showCreateModal = ref(false)
const createAnalysisId = ref(null)
const createFormat = ref('GeoTIFF')
const isCreating = ref(false)
const createError = ref('')

async function loadInitialData() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [projectsRes, analysesRes] = await Promise.all([api.get('projects'), api.get('analyses')])
    projects.value = projectsRes.data
    analyses.value = analysesRes.data

    if (route.query.analysis) {
      const id = Number(route.query.analysis)
      const match = analyses.value.find((a) => a.id === id)
      if (match) {
        filterAnalysisId.value = id
        filterProjectId.value = match.project_id
      }
    }

    await fetchExports()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load exports.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadInitialData)

async function fetchExports() {
  try {
    const params = {}
    if (filterProjectId.value) params.project_id = filterProjectId.value
    if (filterAnalysisId.value) params.analysis_id = filterAnalysisId.value
    if (filterType.value) params.type = filterType.value
    const { data } = await api.get('exports', { params })
    exports.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load exports.'
  }
}

watch([filterProjectId, filterAnalysisId, filterType], fetchExports)

const filteredAnalysesForFilter = computed(() =>
  filterProjectId.value ? analyses.value.filter((a) => a.project_id === filterProjectId.value) : analyses.value
)

const completedAnalyses = computed(() => analyses.value.filter((a) => a.status === 'Completed'))

function openCreateModal() {
  createAnalysisId.value = completedAnalyses.value[0]?.id ?? null
  createFormat.value = 'GeoTIFF'
  createError.value = ''
  showCreateModal.value = true
}

async function createExport() {
  isCreating.value = true
  createError.value = ''
  try {
    await api.post('exports', { analysis_id: createAnalysisId.value, type: createFormat.value })
    showCreateModal.value = false
    await fetchExports()
  } catch (error) {
    createError.value = error.response?.data?.detail || 'Unable to create this export.'
  } finally {
    isCreating.value = false
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
    errorMessage.value = 'Unable to download this file.'
  }
}

async function deleteExport(exp) {
  if (!confirm(`Delete ${exp.file_name}?`)) return
  try {
    await api.delete(`exports/${exp.id}`)
    exports.value = exports.value.filter((e) => e.id !== exp.id)
  } catch (error) {
    errorMessage.value = 'Unable to delete this export.'
  }
}

function formatSize(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Processing') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}
</script>
