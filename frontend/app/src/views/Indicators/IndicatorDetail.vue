<template>
  <WorkspaceShell
    :title="indicator ? `${indicator.icon || ''} ${indicator.name}`.trim() : 'Indicator'"
    :subtitle="indicator ? indicator.description : ''"
  >
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push('/indicators')">
        ← Back to Indicators
      </button>
      <button
        class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-50"
        :disabled="!indicator || !indicator.supported_dataset || indicator.supported_dataset === 'Not yet supported'"
        @click="router.push(`/analysis/new?indicator=${indicator.id}`)"
      >
        Run Analysis
      </button>
    </template>

    <section class="mx-auto max-w-3xl space-y-6">
      <p v-if="errorMessage" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div v-if="isLoading" class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">
        Loading indicator…
      </div>

      <template v-else-if="indicator">
        <p v-if="isUnsupported" class="rounded-2xl border border-amber-100 bg-amber-50/70 px-4 py-3 text-sm font-semibold text-amber-700">
          This indicator isn't wired to real computation yet — running it will fail with a clear message rather than fabricate a result.
        </p>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Description</h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-600">{{ indicator.documentation || indicator.description }}</p>
        </div>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Formula</h2>
          <p class="mt-2 rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3 font-mono text-sm text-slate-700">{{ indicator.formula || '—' }}</p>
        </div>

        <div class="grid gap-6 sm:grid-cols-2">
          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Dataset</h2>
            <div class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="ds in datasetList"
                :key="ds"
                class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
              >
                {{ ds }}
              </span>
            </div>
            <p class="mt-3 text-xs text-slate-500"><span class="font-semibold text-slate-600">Resolution:</span> {{ indicator.default_resolution || '—' }}</p>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Applications</h2>
            <ul class="mt-3 space-y-1.5 text-sm text-slate-600">
              <li v-for="app in applicationList" :key="app" class="flex items-start gap-2">
                <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#6366f1]"></span>
                {{ app }}
              </li>
            </ul>
          </div>
        </div>

        <div v-if="paletteColors.length" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Preview</h2>
          <p class="mt-1 text-sm text-slate-500">Color legend used to render this indicator on the map.</p>
          <div class="mt-4 h-4 w-full rounded-full" :style="{ background: gradientCss }"></div>
          <div class="mt-2 flex justify-between text-xs font-semibold text-slate-500">
            <span>{{ indicator.min_value }}{{ indicator.unit ? ` ${indicator.unit}` : '' }}</span>
            <span>{{ indicator.max_value }}{{ indicator.unit ? ` ${indicator.unit}` : '' }}</span>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Parameters</h2>
          <p class="mt-1 text-sm text-slate-500">Configured when you run an analysis with this indicator.</p>
          <div class="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
            <p><span class="block text-xs font-semibold text-slate-500">Cloud Cover</span>Optional, %</p>
            <p><span class="block text-xs font-semibold text-slate-500">Date Range</span>Start / End date</p>
            <p><span class="block text-xs font-semibold text-slate-500">Resolution</span>{{ indicator.default_resolution || '—' }}</p>
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
import api from '@/services/api'

const route = useRoute()
const router = useRouter()

const indicator = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

async function fetchIndicator() {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const { data } = await api.get(`indicators/${route.params.id}`)
    indicator.value = data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load this indicator.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchIndicator)

const isUnsupported = computed(() => !indicator.value?.supported_dataset || indicator.value.supported_dataset === 'Not yet supported')

const datasetList = computed(() => (indicator.value?.supported_dataset || '—').split(',').map((s) => s.trim()))
const applicationList = computed(() => (indicator.value?.applications || '').split(',').map((s) => s.trim()).filter(Boolean))

const paletteColors = computed(() => {
  if (!indicator.value?.color_palette) return []
  try {
    return JSON.parse(indicator.value.color_palette)
  } catch {
    return []
  }
})

const gradientCss = computed(() => `linear-gradient(90deg, ${paletteColors.value.join(', ')})`)
</script>
