<template>
  <WorkspaceShell
    title="Favorites"
    subtitle="Your saved analyses, for quick access."
  >
    <template #actions>
      <label class="relative">
        <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="7" />
          <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Search favorite…"
          class="w-64 rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-[#6366f1]"
        />
      </label>
    </template>

    <section>
      <p v-if="errorMessage" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div class="mb-6 flex flex-wrap gap-2">
        <button
          v-for="f in indicatorFilters"
          :key="f"
          class="rounded-full px-4 py-1.5 text-xs font-semibold transition"
          :class="activeFilter === f ? 'bg-[#6366f1] text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
          @click="activeFilter = f"
        >
          {{ f }}
        </button>
      </div>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading favorites…
      </div>

      <div v-else-if="filtered.length === 0" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm">
        <div class="mx-auto max-w-sm">
          <div class="text-5xl">⭐</div>
          <h3 class="mt-4 text-lg font-bold text-slate-900">No favorites yet</h3>
          <p class="mt-2 text-sm text-slate-500">Save analyses from their result page to access them quickly here.</p>
        </div>
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="fav in filtered" :key="fav.id" class="flex flex-col justify-between rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
          <div>
            <div class="flex items-start justify-between gap-3">
              <p class="text-sm font-bold text-slate-900">⭐ {{ fav.indicator_name }}</p>
              <span class="whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(fav.analysis_status)">{{ fav.analysis_status }}</span>
            </div>
            <p class="mt-2 text-sm text-slate-600">{{ fav.project_name || '—' }}</p>
            <div class="mt-4 space-y-1 text-xs text-slate-500">
              <p>{{ fav.dataset_name || '—' }}</p>
              <p>{{ formatDate(fav.analysis_created_at) }}</p>
            </div>
          </div>

          <div class="mt-5 flex items-center gap-2 border-t border-slate-100 pt-4">
            <button class="flex-1 rounded-xl bg-[#eef2ff] px-3 py-2 text-xs font-semibold text-[#4f46e5] transition hover:bg-[#e0e7ff]" @click="openAnalysis(fav)">
              Open
            </button>
            <button
              class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="!fav.export_id"
              :title="fav.export_id ? '' : 'No completed export for this analysis yet'"
              @click="downloadExport(fav)"
            >
              Download
            </button>
            <button class="rounded-xl border border-rose-100 px-3 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50" @click="removeFavorite(fav)">
              Remove
            </button>
          </div>
        </article>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import api from '@/services/api'

const router = useRouter()

const favorites = ref([])
const isLoading = ref(true)
const errorMessage = ref('')
const search = ref('')
const activeFilter = ref('All')

async function fetchFavorites() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get('favorites')
    favorites.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load favorites.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchFavorites)

const indicatorFilters = computed(() => ['All', ...new Set(favorites.value.map((f) => f.indicator_name))])

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return favorites.value.filter((f) => {
    if (activeFilter.value !== 'All' && f.indicator_name !== activeFilter.value) return false
    if (!q) return true
    return f.indicator_name.toLowerCase().includes(q) || (f.project_name || '').toLowerCase().includes(q)
  })
})

function openAnalysis(fav) {
  router.push(`/projects/${fav.project_id}/analysis/${fav.analysis_id}`)
}

async function downloadExport(fav) {
  try {
    const { data } = await api.get(`exports/download/${fav.export_id}`, { responseType: 'blob' })
    const url = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = `${fav.indicator_name}`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    errorMessage.value = 'Unable to download this file.'
  }
}

async function removeFavorite(fav) {
  try {
    await api.delete(`favorites/${fav.id}`)
    favorites.value = favorites.value.filter((f) => f.id !== fav.id)
  } catch (error) {
    errorMessage.value = 'Unable to remove this favorite.'
  }
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
