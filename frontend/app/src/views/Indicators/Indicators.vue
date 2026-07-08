<template>
  <WorkspaceShell
    title="Indicators"
    subtitle="Browse and explore the geospatial indicators available for analysis."
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
          placeholder="Search indicator…"
          class="w-64 rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-[#6366f1]"
        />
      </label>
    </template>

    <section>
      <p v-if="errorMessage" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div class="mb-6 flex flex-wrap gap-2">
        <button
          v-for="cat in categories"
          :key="cat"
          class="rounded-full px-4 py-1.5 text-xs font-semibold transition"
          :class="activeCategory === cat ? 'bg-[#6366f1] text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300'"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading indicators…
      </div>

      <div v-else-if="filtered.length === 0" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        No indicators match your search.
      </div>

      <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="indicator in filtered"
          :key="indicator.id"
          class="flex flex-col justify-between rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ indicator.icon || '📊' }}</span>
              <h2 class="text-lg font-bold text-slate-900">{{ indicator.name }}</h2>
            </div>
            <p class="mt-2 text-sm leading-relaxed text-slate-500">{{ indicator.description }}</p>

            <div class="mt-4 space-y-1.5 text-xs text-slate-500">
              <p><span class="font-semibold text-slate-600">Category:</span> {{ indicator.category }}</p>
              <p><span class="font-semibold text-slate-600">Dataset:</span> {{ indicator.supported_dataset || '—' }}</p>
              <p><span class="font-semibold text-slate-600">Resolution:</span> {{ indicator.default_resolution || '—' }}</p>
            </div>
          </div>

          <div class="mt-5 flex items-center gap-2 border-t border-slate-100 pt-4">
            <button class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50" @click="router.push(`/indicators/${indicator.id}`)">
              View Details
            </button>
            <button class="flex-1 rounded-xl bg-[#eef2ff] px-3 py-2 text-xs font-semibold text-[#4f46e5] transition hover:bg-[#e0e7ff]" @click="router.push(`/analysis/new?indicator=${indicator.id}`)">
              Run Analysis
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

const indicators = ref([])
const isLoading = ref(true)
const errorMessage = ref('')
const search = ref('')
const activeCategory = ref('All')

async function fetchIndicators() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get('indicators')
    indicators.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load indicators.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchIndicators)

const categories = computed(() => ['All', ...new Set(indicators.value.map((i) => i.category))])

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return indicators.value.filter((i) => {
    if (activeCategory.value !== 'All' && i.category !== activeCategory.value) return false
    if (!q) return true
    return i.name.toLowerCase().includes(q) || (i.description || '').toLowerCase().includes(q)
  })
})
</script>
