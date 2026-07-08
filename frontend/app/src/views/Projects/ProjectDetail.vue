<template>
  <WorkspaceShell
    :title="project ? project.name : 'Loading…'"
    :subtitle="project ? (project.description || 'No description provided.') : ''"
  >
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push('/projects')">
        ← Back to Projects
      </button>
      <button
        class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-50"
        :disabled="!project"
        @click="router.push(`/analysis/new?project=${project.id}`)"
      >
        + New Analysis
      </button>
    </template>

    <section>
      <p v-if="errorMessage" class="mb-5 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">
        {{ errorMessage }}
      </p>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading project…
      </div>

      <template v-else-if="project">
        <div class="mb-6 flex gap-1 rounded-xl bg-white p-1 shadow-sm border border-slate-100 w-fit">
          <button
            v-for="tab in tabs"
            :key="tab"
            class="rounded-lg px-4 py-1.5 text-sm font-semibold transition"
            :class="tab === activeTab ? 'bg-[#6366f1] text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </div>

        <!-- OVERVIEW -->
        <div v-if="activeTab === 'Overview'" class="space-y-6">
          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="card in stats" :key="card.label" class="rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm">
              <p class="text-sm text-slate-500">{{ card.label }}</p>
              <p class="mt-2 text-2xl font-black tracking-tight text-slate-900">{{ card.value }}</p>
            </article>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Project Information</h2>
            <p class="mt-1 text-sm text-slate-500">{{ project.description || 'No description provided.' }}</p>
            <div class="mt-4 grid gap-4 text-sm text-slate-600 md:grid-cols-2">
              <p><span class="font-semibold text-slate-500">Created At:</span> {{ project.created }}</p>
              <p><span class="font-semibold text-slate-500">Area:</span> {{ project.area ? `${project.area} ha` : 'Not set' }}</p>
              <p>
                <span class="font-semibold text-slate-500">Status:</span>
                <span class="ml-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass(project.statusLabel)">{{ project.statusLabel }}</span>
              </p>
              <p><span class="font-semibold text-slate-500">AOI:</span> {{ project.geometry ? 'Polygon defined' : 'Not set' }}</p>
            </div>
          </div>

          <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <div class="mb-3 flex items-center justify-between">
                <h2 class="text-lg font-bold text-slate-900">AOI Map</h2>
                <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">{{ project.area ? `${project.area} ha` : 'No AOI' }}</span>
              </div>
              <ProjectAoiMap :center="mapCenter" :polygon="mapPolygon" class="h-[280px] rounded-[20px] overflow-hidden" />
            </div>

            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Quick Actions</h2>
              <div class="mt-4 grid gap-3">
                <button class="rounded-2xl bg-[#6366f1] px-4 py-3 text-left text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="router.push(`/analysis/new?project=${project.id}`)">
                  ▶ Run Analysis
                </button>
                <button class="rounded-2xl border border-slate-200 px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:bg-slate-50" @click="activeTab = 'Map'">
                  ⤒ Update AOI
                </button>
                <button class="rounded-2xl border border-slate-200 px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:bg-slate-50" @click="activeTab = 'Exports'">
                  ⤓ Export
                </button>
                <button class="rounded-2xl border border-rose-100 px-4 py-3 text-left text-sm font-semibold text-rose-500 transition hover:bg-rose-50" @click="deleteProject()">
                  🗑 Delete Project
                </button>
              </div>
            </div>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <h2 class="text-lg font-bold text-slate-900">Recent Analyses</h2>
              <button class="text-sm font-semibold text-[#6366f1] transition hover:text-[#4f46e5]" @click="activeTab = 'Analyses'">View all →</button>
            </div>
            <p v-if="project.analyses.length === 0" class="py-6 text-center text-sm text-slate-500">No analyses yet — run your first one.</p>
            <div v-else class="grid gap-3 md:grid-cols-2">
              <div
                v-for="analysis in project.analyses.slice(0, 4)"
                :key="analysis.id"
                class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-slate-200 hover:bg-slate-50"
                @click="router.push(`/projects/${project.id}/analysis/${analysis.id}`)"
              >
                <div>
                  <p class="text-sm font-semibold text-slate-800">{{ analysis.name }}</p>
                  <p class="mt-1 text-xs text-slate-500">{{ analysis.date }}</p>
                </div>
                <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="analysisStatusClass(analysis.status)">{{ analysis.status }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- MAP -->
        <div v-else-if="activeTab === 'Map'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-bold text-slate-900">AOI Map</h2>
              <p class="text-sm text-slate-500">{{ project.geometry ? 'Polygon imported for this project.' : 'No AOI set for this project yet.' }}</p>
            </div>
            <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">{{ project.area ? `${project.area} ha` : 'No AOI' }}</span>
          </div>
          <ProjectAoiMap :center="mapCenter" :polygon="mapPolygon" class="h-[520px] rounded-[20px] overflow-hidden" />
        </div>

        <!-- ANALYSES -->
        <div v-else-if="activeTab === 'Analyses'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-slate-900">Analyses</h2>
            <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="router.push(`/analysis/new?project=${project.id}`)">+ New Analysis</button>
          </div>
          <p v-if="project.analyses.length === 0" class="py-10 text-center text-sm text-slate-500">No analyses yet — run your first one.</p>
          <div v-else class="space-y-3">
            <div
              v-for="analysis in project.analyses"
              :key="analysis.id"
              class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-slate-200 hover:bg-slate-50"
              @click="router.push(`/projects/${project.id}/analysis/${analysis.id}`)"
            >
              <div>
                <p class="text-sm font-semibold text-slate-800">{{ analysis.name }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ analysis.date }}</p>
              </div>
              <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="analysisStatusClass(analysis.status)">{{ analysis.status }}</span>
            </div>
          </div>
        </div>

        <!-- EXPORTS -->
        <div v-else-if="activeTab === 'Exports'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Exports</h2>
          <p v-if="project.exports.length === 0" class="mt-4 py-10 text-center text-sm text-slate-500">No exports yet.</p>
          <div v-else class="mt-4 space-y-3">
            <div
              v-for="item in project.exports"
              :key="item"
              class="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 p-4 text-sm font-semibold text-slate-700 transition hover:border-slate-200 hover:bg-slate-50"
            >
              {{ item }}
              <span class="text-xs font-semibold text-[#6366f1] cursor-pointer">Download</span>
            </div>
          </div>
        </div>

        <!-- SETTINGS -->
        <div v-else-if="activeTab === 'Settings'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Project Settings</h2>

          <p v-if="settingsError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">
            {{ settingsError }}
          </p>
          <p v-if="settingsSaved" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">
            Changes saved.
          </p>

          <div class="mt-4 max-w-lg space-y-3">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Project Name</span>
              <input v-model="settingsForm.name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Description</span>
              <textarea v-model="settingsForm.description" rows="3" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]"></textarea>
            </label>
          </div>

          <div class="mt-6 flex gap-3">
            <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60" :disabled="isSavingSettings" @click="saveSettings()">
              {{ isSavingSettings ? 'Saving…' : 'Save changes' }}
            </button>
          </div>

          <div class="mt-8 rounded-2xl border border-rose-100 bg-rose-50/60 p-4">
            <h3 class="text-sm font-bold text-rose-700">Danger zone</h3>
            <p class="mt-1 text-xs text-rose-500">Deleting a project removes all its analyses and exports permanently.</p>
            <button class="mt-3 rounded-xl border border-rose-200 bg-white px-4 py-2 text-sm font-semibold text-rose-600 transition hover:bg-rose-50" @click="deleteProject()">
              Delete Project
            </button>
          </div>
        </div>
      </template>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import ProjectAoiMap from '@/components/Map/ProjectAoiMap.vue'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const STATUS_TO_LABEL = { Running: 'Active', Completed: 'Completed', Archived: 'Archived' }

const tabs = ['Overview', 'Map', 'Analyses', 'Exports', 'Settings']
const activeTab = ref('Overview')

const project = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const settingsForm = ref({ name: '', description: '' })
const isSavingSettings = ref(false)
const settingsError = ref('')
const settingsSaved = ref(false)

async function fetchProject() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [projectRes, analysesRes] = await Promise.all([
      api.get(`projects/${route.params.id}`),
      api.get('analyses', { params: { project_id: route.params.id } }),
    ])
    const data = projectRes.data
    project.value = {
      id: data.id,
      name: data.name,
      description: data.description,
      created: new Date(data.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      area: data.area ? Math.round(data.area * 100) / 100 : null,
      geometry: data.geometry ? JSON.parse(data.geometry) : null,
      statusLabel: STATUS_TO_LABEL[data.status] || data.status,
      analyses: analysesRes.data.map((a) => ({
        id: a.id,
        name: a.name,
        date: new Date(a.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
        status: a.status,
      })),
      exports: [],
    }
    settingsForm.value = { name: data.name, description: data.description || '' }
  } catch (error) {
    errorMessage.value = error.response?.status === 404
      ? 'Project not found.'
      : error.response?.data?.detail || 'Unable to load this project.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchProject)
watch(() => route.params.id, fetchProject)

const stats = computed(() => [
  { label: 'Area', value: project.value.area ? `${project.value.area} ha` : '—' },
  { label: 'Analyses', value: String(project.value.analyses.length) },
  { label: 'Favorites', value: '0' },
  { label: 'Exports', value: String(project.value.exports.length) },
])

const mapCenter = computed(() => {
  if (!project.value?.geometry) return [31.5, -6.5]
  const ring = project.value.geometry.type === 'Polygon' ? project.value.geometry.coordinates[0] : project.value.geometry.coordinates[0][0]
  const lats = ring.map((c) => c[1])
  const lngs = ring.map((c) => c[0])
  return [(Math.min(...lats) + Math.max(...lats)) / 2, (Math.min(...lngs) + Math.max(...lngs)) / 2]
})

const mapPolygon = computed(() => {
  if (!project.value?.geometry) return []
  const ring = project.value.geometry.type === 'Polygon' ? project.value.geometry.coordinates[0] : project.value.geometry.coordinates[0][0]
  return ring.map(([lng, lat]) => [lat, lng])
})

function statusClass(status) {
  if (status === 'Active') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Completed') return 'bg-sky-50 text-sky-700'
  return 'bg-slate-100 text-slate-500'
}

function analysisStatusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  return 'bg-rose-50 text-rose-600'
}

async function saveSettings() {
  isSavingSettings.value = true
  settingsError.value = ''
  settingsSaved.value = false
  try {
    const { data } = await api.put(`projects/${project.value.id}`, {
      name: settingsForm.value.name,
      description: settingsForm.value.description,
    })
    project.value.name = data.name
    project.value.description = data.description
    settingsSaved.value = true
  } catch (error) {
    settingsError.value = error.response?.data?.detail || 'Unable to save changes.'
  } finally {
    isSavingSettings.value = false
  }
}

async function deleteProject() {
  if (!confirm('Delete this project? This cannot be undone.')) return
  try {
    await api.delete(`projects/${project.value.id}`)
    router.push('/projects')
  } catch (error) {
    alert(error.response?.data?.detail || 'Unable to delete project.')
  }
}
</script>
