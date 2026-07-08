<template>
  <WorkspaceShell
    title="Dashboard"
    subtitle="GeoInsight workspace overview, project activity, and spatial insights in one place."
  >
    <template #actions>
      <button class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50">
        New Project
      </button>
      <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]">
        Run Analysis
      </button>
    </template>

    <section>
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
            <div class="mt-3 flex items-end justify-between gap-3">
              <div>
                <h3 class="text-2xl font-black tracking-tight text-slate-900">{{ card.value }}</h3>
                <p class="mt-1 text-xs text-slate-400">{{ card.description }}</p>
              </div>
              <span
                class="flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold"
                :class="card.trendUp ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-500'"
              >
                <span>{{ card.trendUp ? '↑' : '↓' }}</span>{{ card.trend }}
              </span>
            </div>
          </article>
        </div>

        <div class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <section class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Interactive Map</h2>
                <p class="text-sm text-slate-500">Spatial workspace preview</p>
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

              <div class="absolute left-1/2 top-1/2 w-[280px] -translate-x-1/2 -translate-y-1/2 rounded-[22px] border border-white bg-white/90 p-4 shadow-xl shadow-slate-200/60 backdrop-blur">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#0ea5ff]">Region</p>
                    <h3 class="mt-1 text-base font-bold text-slate-900">Casablanca North</h3>
                  </div>
                  <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">8 layers</span>
                </div>
                <div class="mt-4 grid grid-cols-2 gap-3 text-sm">
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-slate-500">Coverage</p>
                    <p class="mt-1 font-bold text-slate-900">92%</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-slate-500">Status</p>
                    <p class="mt-1 font-bold text-slate-900">Ready</p>
                  </div>
                </div>
              </div>

              <div class="absolute bottom-4 right-4 flex flex-col overflow-hidden rounded-2xl border border-white bg-white shadow-lg">
                <button class="px-3 py-2 text-slate-600 hover:bg-slate-50">+</button>
                <div class="h-px bg-slate-100"></div>
                <button class="px-3 py-2 text-slate-600 hover:bg-slate-50">−</button>
              </div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <div class="mb-4 flex items-center justify-between">
              <div>
                <h2 class="text-lg font-bold text-slate-900">Analysis Overview</h2>
                <p class="text-sm text-slate-500">Recent output and KPI summary</p>
              </div>
              <span class="rounded-full bg-[#f5f3ff] px-3 py-1 text-xs font-semibold text-[#6d28d9]">Updated 2m ago</span>
            </div>

            <div class="space-y-3">
              <article
                v-for="item in analysisCards"
                :key="item.label"
                class="rounded-2xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-slate-200 hover:bg-slate-50"
              >
                <div class="flex items-center justify-between gap-4">
                  <div>
                    <p class="text-sm font-semibold text-slate-700">{{ item.label }}</p>
                    <p class="text-xs text-slate-500">{{ item.note }}</p>
                  </div>
                  <p class="text-xl font-black tracking-tight text-slate-900">{{ item.value }}</p>
                </div>
                <div class="mt-3 h-2 rounded-full bg-slate-200">
                  <div class="h-2 rounded-full" :class="item.barClass" :style="{ width: item.percent }"></div>
                </div>
              </article>
            </div>

            <div class="mt-5 rounded-[22px] bg-slate-900 p-4 text-white">
              <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Pipeline</p>
              <div class="mt-3 flex items-center justify-between">
                <div>
                  <p class="text-sm text-slate-300">Queued jobs</p>
                  <p class="text-3xl font-black">04</p>
                </div>
                <button class="rounded-xl bg-white px-3 py-2 text-sm font-semibold text-slate-900">Open queue</button>
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
              <button class="text-sm font-semibold text-[#6366f1] transition hover:text-[#4f46e5]">View all →</button>
            </div>

            <div class="overflow-hidden rounded-[22px] border border-slate-100">
              <table class="w-full text-left text-sm">
                <thead class="bg-slate-50 text-slate-500">
                  <tr>
                    <th class="px-4 py-3 font-medium">Name</th>
                    <th class="px-4 py-3 font-medium">Region</th>
                    <th class="px-4 py-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="project in recentProjects" :key="project.name" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                    <td class="px-4 py-4 font-medium text-slate-800">{{ project.name }}</td>
                    <td class="px-4 py-4 text-slate-500">{{ project.region }}</td>
                    <td class="px-4 py-4">
                      <span class="rounded-full px-3 py-1 text-xs font-semibold" :class="project.badgeClass">
                        {{ project.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
            <h2 class="text-lg font-bold text-slate-900">Quick Actions</h2>
            <p class="text-sm text-slate-500">Jump to the most common tasks</p>

            <div class="mt-4 grid gap-3">
              <button class="rounded-2xl bg-[#6366f1] px-4 py-3 text-left text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] hover:shadow-md">+ Create project</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">Upload AOI</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">Open API Explorer</button>
              <button class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50">Export results</button>
            </div>
          </div>
        </section>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'

const metricCards = [
  {
    title: 'Projects',
    value: '12',
    description: 'Active spatial workspaces',
    icon: '🗂️',
    iconBg: 'bg-[#eef2ff]',
    trend: '3 this week',
    trendUp: true,
  },
  {
    title: 'Analyses',
    value: '54',
    description: 'Completed processing jobs',
    icon: '📊',
    iconBg: 'bg-[#eff6ff]',
    trend: '12%',
    trendUp: true,
  },
  {
    title: 'Favorites',
    value: '8',
    description: 'Pinned layers and reports',
    icon: '⭐',
    iconBg: 'bg-amber-50',
    trend: '2 new',
    trendUp: true,
  },
  {
    title: 'Avg. processing time',
    value: '1m 42s',
    description: 'Across the last 30 analyses',
    icon: '⏱️',
    iconBg: 'bg-violet-50',
    trend: '8%',
    trendUp: false,
  },
  {
    title: 'Storage',
    value: '1.4 GB',
    description: 'Used from the cloud quota',
    icon: '☁️',
    iconBg: 'bg-slate-50',
    trend: '5%',
    trendUp: false,
  },
]

const analysisCards = [
  {
    label: 'NDVI Pipeline',
    note: 'Latest vegetation indices generated',
    value: '91%',
    percent: '91%',
    barClass: 'bg-emerald-500',
  },
  {
    label: 'Land Cover Classification',
    note: 'Random forest model ready',
    value: '84%',
    percent: '84%',
    barClass: 'bg-[#6366f1]',
  },
  {
    label: 'Change Detection',
    note: 'Pending tile export',
    value: '62%',
    percent: '62%',
    barClass: 'bg-sky-500',
  },
]

const recentProjects = [
  {
    name: 'Flood Risk Morocco',
    region: 'Rabat-Salé-Kénitra',
    status: 'Completed',
    badgeClass: 'bg-emerald-50 text-emerald-700',
  },
  {
    name: 'NDVI Casablanca',
    region: 'Casablanca-Settat',
    status: 'Running',
    badgeClass: 'bg-amber-50 text-amber-700',
  },
  {
    name: 'Forest Biomass',
    region: 'Maâmora',
    status: 'Queued',
    badgeClass: 'bg-slate-100 text-slate-600',
  },
]
</script>
