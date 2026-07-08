<template>
  <WorkspaceShell title="Projects" subtitle="Manage all your GIS projects in one place.">
    <template #actions>
      <label class="relative">
        <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="7" />
          <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Search projects…"
          class="w-56 rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-[#6366f1]"
        />
      </label>
      <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openNewProject()">
        + New Project
      </button>
    </template>

    <section>
      <p v-if="errorMessage" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">
        {{ errorMessage }}
      </p>

      <div class="mb-5 flex items-center justify-between">
        <div class="flex gap-1 rounded-xl bg-white p-1 shadow-sm border border-slate-100">
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
        <p class="text-sm text-slate-500">{{ filtered.length }} project{{ filtered.length === 1 ? '' : 's' }}</p>
      </div>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading projects…
      </div>

      <div v-else-if="filtered.length === 0" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm">
        <div class="mx-auto max-w-sm">
          <div class="text-5xl">📁</div>
          <h3 class="mt-4 text-lg font-bold text-slate-900">No projects found</h3>
          <p class="mt-2 text-sm text-slate-500">Try a different search or create your first GIS project.</p>
          <button class="mt-6 rounded-2xl bg-[#6366f1] px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openNewProject()">
            + Create Project
          </button>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="project in filtered"
          :key="project.id"
          class="flex flex-col justify-between rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div>
            <div class="flex items-start justify-between gap-3">
              <h3 class="text-base font-bold text-slate-900">{{ project.name }}</h3>
              <span class="flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(project.statusLabel)">
                <span class="h-1.5 w-1.5 rounded-full" :class="statusDotClass(project.statusLabel)"></span>
                {{ project.statusLabel }}
              </span>
            </div>
            <p class="mt-1.5 text-sm text-slate-500">{{ project.description || 'No description provided.' }}</p>

            <div class="mt-4 space-y-1.5 text-xs text-slate-500">
              <p>📅 {{ project.created }}</p>
              <p>🗺️ AOI: {{ project.area ? `${project.area} ha` : 'Not set' }}</p>
              <p>📊 {{ project.analyses }} Analyses</p>
            </div>
          </div>

          <div class="mt-5 flex items-center gap-2 border-t border-slate-100 pt-4">
            <button class="flex-1 rounded-xl bg-[#eef2ff] px-3 py-2 text-xs font-semibold text-[#4f46e5] transition hover:bg-[#e0e7ff]" @click="openProject(project.id)">
              Open
            </button>
            <button class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50" @click="editProject(project)">
              Edit
            </button>
            <button class="rounded-xl border border-rose-100 px-3 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50" @click="deleteProject(project.id)">
              Delete
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- New / Edit Project Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeModal()">
      <div class="w-full max-w-3xl rounded-[28px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">{{ editingId ? 'Edit Project' : 'Create New Project' }}</h3>
        <p class="mt-1 text-sm text-slate-500">Provide project details and an area of interest.</p>

        <p v-if="modalError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">
          {{ modalError }}
        </p>

        <div class="mt-5 grid gap-6 md:grid-cols-2">
          <div class="space-y-3">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Project Name</span>
              <input v-model="form.name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" placeholder="e.g. Flood Risk Assessment" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Description</span>
              <textarea v-model="form.description" rows="3" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" placeholder="Short description of the project"></textarea>
            </label>

            <div>
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Area of Interest</span>
              <div class="flex gap-1 rounded-xl bg-slate-50 p-1">
                <button
                  type="button"
                  class="flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition"
                  :class="aoiTab === 'draw' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                  @click="aoiTab = 'draw'"
                >
                  Draw on Map
                </button>
                <button
                  type="button"
                  class="flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold transition"
                  :class="aoiTab === 'upload' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                  @click="aoiTab = 'upload'"
                >
                  Upload Shapefile
                </button>
              </div>

              <div v-if="aoiTab === 'upload'" class="mt-3 rounded-xl border border-dashed border-slate-200 bg-slate-50/70 p-4 text-center">
                <input ref="fileInput" type="file" accept=".zip" class="hidden" @change="handleShapefileUpload" />
                <button type="button" class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-50" @click="fileInput.click()">
                  Choose .zip file
                </button>
                <p class="mt-2 text-[11px] text-slate-400">Zip containing .shp, .shx, .dbf (and .prj)</p>
                <p v-if="isUploadingShapefile" class="mt-2 text-xs font-semibold text-[#6366f1]">Parsing shapefile…</p>
              </div>

              <p v-if="form.area" class="mt-2 text-xs font-semibold text-emerald-600">
                ✓ AOI set — {{ form.area }} ha
              </p>
            </div>
          </div>

          <div v-show="aoiTab === 'draw'" class="h-[320px] overflow-hidden rounded-2xl border border-slate-200">
            <AoiDrawer @change="onAoiDrawn" />
          </div>
          <div v-if="aoiTab === 'upload'" class="flex h-[320px] items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-sm text-slate-400">
            Upload a shapefile to preview it on the map.
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="closeModal()">Cancel</button>
          <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60" :disabled="isSaving" @click="saveProject()">
            {{ isSaving ? 'Saving…' : editingId ? 'Save changes' : 'Create' }}
          </button>
        </div>
      </div>
    </div>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import AoiDrawer from '@/components/Map/AoiDrawer.vue'
import api from '@/services/api'

const router = useRouter()

const STATUS_TO_LABEL = { Running: 'Active', Completed: 'Completed', Archived: 'Archived' }
const LABEL_TO_STATUS = { Active: 'Running', Completed: 'Completed', Archived: 'Archived' }

const tabs = ['All', 'Active', 'Completed', 'Archived']
const activeTab = ref('All')
const search = ref('')
const showModal = ref(false)
const editingId = ref(null)
const aoiTab = ref('draw')
const fileInput = ref(null)
const isLoading = ref(false)
const isSaving = ref(false)
const isUploadingShapefile = ref(false)
const errorMessage = ref('')
const modalError = ref('')

const form = ref({ name: '', description: '', geometry: null, area: null })

const projects = ref([])

async function fetchProjects() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get('projects')
    projects.value = data.map(mapProject)
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load projects.'
  } finally {
    isLoading.value = false
  }
}

function mapProject(p) {
  return {
    id: p.id,
    name: p.name,
    description: p.description,
    created: new Date(p.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
    analyses: 0,
    area: p.area ? Math.round(p.area * 100) / 100 : null,
    geometry: p.geometry ? JSON.parse(p.geometry) : null,
    statusLabel: STATUS_TO_LABEL[p.status] || p.status,
  }
}

onMounted(fetchProjects)

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return projects.value.filter((p) => {
    if (activeTab.value !== 'All' && p.statusLabel !== activeTab.value) return false
    if (!q) return true
    return p.name.toLowerCase().includes(q)
  })
})

function statusClass(status) {
  if (status === 'Active') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Completed') return 'bg-sky-50 text-sky-700'
  return 'bg-slate-100 text-slate-500'
}

function statusDotClass(status) {
  if (status === 'Active') return 'bg-emerald-500'
  if (status === 'Completed') return 'bg-sky-500'
  return 'bg-slate-400'
}

function openProject(id) {
  router.push(`/projects/${id}`)
}

function editProject(project) {
  editingId.value = project.id
  form.value = { name: project.name, description: project.description || '', geometry: project.geometry, area: project.area }
  aoiTab.value = 'draw'
  modalError.value = ''
  showModal.value = true
}

async function deleteProject(id) {
  if (!confirm('Delete this project? This cannot be undone.')) return
  try {
    await api.delete(`projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
  } catch (error) {
    alert(error.response?.data?.detail || 'Unable to delete project.')
  }
}

function openNewProject() {
  editingId.value = null
  form.value = { name: '', description: '', geometry: null, area: null }
  aoiTab.value = 'draw'
  modalError.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function onAoiDrawn({ geometry, areaHa }) {
  form.value.geometry = geometry
  form.value.area = geometry ? Math.round(areaHa * 100) / 100 : null
}

async function handleShapefileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  isUploadingShapefile.value = true
  modalError.value = ''
  try {
    const payload = new FormData()
    payload.append('file', file)
    const { data } = await api.post('projects/aoi/shapefile', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.value.geometry = data.geometry
    form.value.area = Math.round(data.area * 100) / 100
  } catch (error) {
    modalError.value = error.response?.data?.detail || 'Unable to parse the shapefile.'
  } finally {
    isUploadingShapefile.value = false
    event.target.value = ''
  }
}

async function saveProject() {
  const name = (form.value.name || '').trim()
  if (!name) {
    modalError.value = 'Please provide a project name'
    return
  }

  isSaving.value = true
  modalError.value = ''
  try {
    const payload = {
      name,
      description: form.value.description || null,
      geometry: form.value.geometry,
      area: form.value.area,
    }

    if (editingId.value) {
      const { data } = await api.put(`projects/${editingId.value}`, payload)
      const index = projects.value.findIndex((p) => p.id === editingId.value)
      if (index !== -1) projects.value[index] = mapProject(data)
    } else {
      const { data } = await api.post('projects', { ...payload, status: 'Running' })
      projects.value.unshift(mapProject(data))
    }

    showModal.value = false
  } catch (error) {
    modalError.value = error.response?.data?.detail || 'Unable to save project.'
  } finally {
    isSaving.value = false
  }
}
</script>
