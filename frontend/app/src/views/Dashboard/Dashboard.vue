<template>
  <WorkspaceShell
    title="Dashboard"
    subtitle="GeoInsight workspace overview, project activity, and spatial insights in one place."
  >
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push('/projects')">
        New Project
      </button>
      <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="router.push('/analysis/new')">
        Run Analysis
      </button>
    </template>

    <section>
      <p v-if="errorMessage" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ errorMessage }}</p>

      <div class="space-y-6">
        <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <article
            v-for="card in metricCards"
            :key="card.title"
            class="group rounded-[24px] border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div class="flex items-center justify-between">
              <p class="text-sm text-slate-500">{{ card.title }}</p>
              <div
                class="flex h-10 w-10 items-center justify-center rounded-2xl text-xl transition group-hover:scale-105"
                :class="card.iconBg"
              >
                {{ card.icon }}
              </div>
            </div>
            <div class="mt-3">
              <h3 class="text-2xl font-black tracking-tight text-slate-900">{{ card.value }}</h3>
              <p class="mt-1 text-xs text-slate-400">{{ card.description }}</p>
            </div>
          </article>
        </div>

        <div class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <section class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Latest Project</h2>
                <p class="text-sm text-slate-500">Most recently created workspace</p>
              </div>
              <span class="flex items-center gap-1.5 rounded-full bg-[#eff6ff] px-3 py-1 text-xs font-semibold text-[#2563eb]">
                <span class="relative flex h-2 w-2">
                  <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#2563eb]/60"></span>
                  <span class="relative inline-flex h-2 w-2 rounded-full bg-[#2563eb]"></span>
                </span>
                Live
              </span>
            </div>

            <div class="relative h-[420px] overflow-hidden rounded-[24px] bg-gradient-to-br from-[#eef4ff] via-white to-[#f8fbff]">
              <div class="absolute inset-0 opacity-60">
                <div class="absolute left-10 top-8 h-16 w-16 rounded-full border border-[#dbeafe]"></div>
                <div class="absolute right-14 top-20 h-24 w-24 rounded-full border border-[#c7d2fe]"></div>
                <div class="absolute bottom-10 left-1/4 h-20 w-20 rounded-full border border-[#bae6fd]"></div>
                <div class="absolute left-1/2 top-1/3 h-1 w-44 -rotate-12 rounded-full bg-[#93c5fd]/70"></div>
                <div class="absolute left-[14%] top-[58%] h-1 w-28 rotate-12 rounded-full bg-[#60a5fa]/50"></div>
                <div class="absolute right-[20%] bottom-[18%] h-1 w-36 -rotate-6 rounded-full bg-[#6366f1]/35"></div>
              </div>

              <div v-if="latestProject" class="absolute left-1/2 top-1/2 w-[280px] -translate-x-1/2 -translate-y-1/2 rounded-[22px] border border-white bg-white/90 p-4 shadow-xl shadow-slate-200/60 backdrop-blur">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#0ea5ff]">Project</p>
                    <h3 class="mt-1 text-base font-bold text-slate-900">{{ latestProject.name }}</h3>
                  </div>
                  <span class="rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusBadgeClass(latestProject.status)">{{ latestProject.status }}</span>
                </div>
                <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-slate-500">Area</p>
                    <p class="mt-1 font-bold text-slate-900">{{ latestProject.area ? `${latestProject.area} ha` : '—' }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-slate-500">Created</p>
                    <p class="mt-1 font-bold text-slate-900">{{ formatDate(latestProject.created_at) }}</p>
                  </div>
                </div>
                <button class="mt-4 w-full rounded-xl bg-[#6366f1] px-3 py-2 text-xs font-semibold text-white transition hover:bg-[#5558e6]" @click="router.push(`/projects/${latestProject.id}`)">
                  Open project →
                </button>
              </div>
              <div v-else class="absolute inset-0 flex items-center justify-center">
                <div class="rounded-[22px] border border-white bg-white/90 px-6 py-5 text-center shadow-xl shadow-slate-200/60 backdrop-blur">
                  <p class="text-sm font-semibold text-slate-500">No projects yet</p>
                  <button class="mt-3 rounded-xl bg-[#6366f1] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#5558e6]" @click="router.push('/projects')">
                    + Create your first project
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Analysis Overview</h2>
                <p class="text-sm text-slate-500">Status breakdown across all analyses</p>
              </div>
            </div>

            <div class="space-y-3">
              <article
                v-for="item in statusBreakdown"
                :key="item.label"
                class="rounded-2xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-slate-200 hover:bg-slate-50"
              >
                <div class="flex items-center justify-between gap-4">
                  <p class="text-sm font-semibold text-slate-700">{{ item.label }}</p>
                  <p class="text-xl font-black tracking-tight text-slate-900">{{ item.count }}</p>
                </div>
                <div class="mt-3 h-2 rounded-full bg-slate-200">
                  <div class="h-2 rounded-full" :class="item.barClass" :style="{ width: item.percent + '%' }"></div>
                </div>
              </article>
              <p v-if="statusBreakdown.every((s) => s.count === 0)" class="py-6 text-center text-sm text-slate-400">No analyses yet.</p>
            </div>

            <div class="mt-5 rounded-[22px] bg-slate-900 p-4 text-white">
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Pipeline</p>
              <div class="mt-3 flex items-center justify-between">
                <div>
                  <p class="text-sm text-slate-300">Running jobs</p>
                  <p class="text-3xl font-black">{{ overview?.running_tasks ?? 0 }}</p>
                </div>
                <button class="rounded-xl bg-white px-3 py-2 text-sm font-semibold text-slate-900" @click="router.push('/statistics')">Open statistics</button>
              </div>
            </div>
          </section>
        </div>

        <section class="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Recent Analyses</h2>
                <p class="text-sm text-slate-500">Latest workspace activity</p>
              </div>
              <button class="text-sm font-semibold text-[#6366f1] transition hover:text-[#4f46e5]" @click="router.push('/statistics')">View all →</button>
            </div>

            <div class="overflow-hidden rounded-[22px] border border-slate-100">
              <table class="w-full text-left text-sm">
                <thead class="bg-slate-50 text-slate-500">
                  <tr>
                    <th class="px-4 py-3 font-medium">Name</th>
                    <th class="px-4 py-3 font-medium">Created</th>
                    <th class="px-4 py-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="analysis in recentAnalyses" :key="analysis.id" class="cursor-pointer border-t border-slate-100 transition hover:bg-slate-50/80" @click="router.push(`/projects/${analysis.project_id}/analysis/${analysis.id}`)">
                    <td class="px-4 py-4 font-medium text-slate-800">{{ analysis.name }}</td>
                    <td class="px-4 py-4 text-slate-500">{{ formatDate(analysis.created_at) }}</td>
                    <td class="px-4 py-4">
                      <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="statusBadgeClass(analysis.status)">
                        {{ analysis.status }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="recentAnalyses.length === 0">
                    <td colspan="3" class="px-4 py-10 text-center text-sm text-slate-400">No analyses yet — run your first one.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Quick Actions</h2>
            <p class="text-sm text-slate-500">Jump to the most common tasks</p>

            <div class="mt-4 grid gap-3">
              <button class="rounded-2xl bg-[#6366f1] px-4 py-3 text-left text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] hover:shadow-md" @click="router.push('/projects')">+ Create project</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50" @click="router.push('/analysis/new')">Run new analysis</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50" @click="router.push('/exports')">Export Center</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50" @click="router.push('/favorites')">View favorites</button>
            </div>
          </div>
        </section>
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

const overview = ref(null)
const statusCounts = ref([])
const projects = ref([])
const analyses = ref([])
const favorites = ref([])
const errorMessage = ref('')

async function loadDashboard() {
  errorMessage.value = ''
  try {
    const [overviewRes, statusRes, projectsRes, analysesRes, favoritesRes] = await Promise.all([
      api.get('statistics/overview'),
      api.get('statistics/status'),
      api.get('projects'),
      api.get('analyses'),
      api.get('favorites'),
    ])
    overview.value = overviewRes.data
    statusCounts.value = statusRes.data
    projects.value = projectsRes.data
    analyses.value = analysesRes.data
    favorites.value = favoritesRes.data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to load dashboard data.'
  }
}

onMounted(loadDashboard)

const latestProject = computed(() => {
  if (!projects.value.length) return null
  return [...projects.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0]
})

const recentAnalyses = computed(() =>
  [...analyses.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5)
)

const metricCards = computed(() => {
  const o = overview.value
  if (!o) return []
  return [
    { title: 'Projects', value: o.projects, description: 'Active spatial workspaces', icon: '🗂️', iconBg: 'bg-[#eef2ff]' },
    { title: 'Analyses', value: o.analyses, description: 'Total processing jobs', icon: '📊', iconBg: 'bg-[#eff6ff]' },
    { title: 'Favorites', value: favorites.value.length, description: 'Pinned analyses', icon: '⭐', iconBg: 'bg-amber-50' },
    { title: 'Avg. processing time', value: o.avg_processing_time != null ? `${o.avg_processing_time.toFixed(1)}s` : '—', description: 'Across completed analyses', icon: '⏱️', iconBg: 'bg-violet-50' },
    { title: 'Exports', value: o.exports, description: 'Generated result files', icon: '📤', iconBg: 'bg-emerald-50' },
  ]
})

const statusBreakdown = computed(() => {
  const total = statusCounts.value.reduce((sum, s) => sum + s.count, 0) || 1
  const byStatus = Object.fromEntries(statusCounts.value.map((s) => [s.status, s.count]))
  const barClasses = { Completed: 'bg-emerald-500', Running: 'bg-amber-500', Failed: 'bg-rose-500', Pending: 'bg-slate-400' }
  return ['Completed', 'Running', 'Failed'].map((status) => {
    const count = byStatus[status] || 0
    return { label: status, count, percent: Math.round((count / total) * 100), barClass: barClasses[status] }
  })
})

function statusBadgeClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  if (status === 'Failed') return 'bg-rose-50 text-rose-600'
  return 'bg-slate-100 text-slate-600'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
