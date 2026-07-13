<template>
  <AdminShell :title="activeTab" subtitle="Platform-wide management — visible to administrators only." v-model:active-tab="activeTab">
    <section>
      <p v-if="!auth.isAdmin && auth.loaded" class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">
        Admin access required.
      </p>

      <template v-else>
        <!-- Dashboard -->
        <div v-if="activeTab === 'Dashboard'" class="space-y-6">
          <div class="relative overflow-hidden rounded-[28px] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
            <div class="pointer-events-none absolute -top-20 -right-7.5 h-56 w-56 rounded-full bg-cyan-400/20 blur-3xl"></div>
            <div class="pointer-events-none absolute -bottom-24 -left-12 h-56 w-56 rounded-full bg-[#6366f1]/20 blur-3xl"></div>

            <div class="relative grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
              <div>
                <p class="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-300">Admin Operations</p>
                <h2 class="mt-2 text-2xl font-black tracking-tight">{{ appSettings?.app_name || 'GeoInsight' }} Control Tower</h2>
                <p class="mt-2 max-w-2xl text-sm text-slate-300">
                  Unified overview of users, projects, analyses, and platform health for day-to-day operations.
                </p>
                <div class="mt-5 flex flex-wrap gap-2">
                  <button class="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold transition hover:bg-white/20" @click="activeTab = 'Users'">Manage Users</button>
                  <button class="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold transition hover:bg-white/20" @click="activeTab = 'Datasets'">Manage Datasets</button>
                  <button class="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold transition hover:bg-white/20" @click="activeTab = 'Indicators'">Manage Indicators</button>
                  <button class="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-semibold transition hover:bg-white/20" @click="activeTab = 'Settings'">System Settings</button>
                </div>
              </div>

              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-300">Today</p>
                <p class="mt-1 text-base font-bold text-white">{{ todayLabel }}</p>
                <div class="mt-3 space-y-2 text-xs">
                  <div class="flex items-center justify-between rounded-lg bg-black/20 px-3 py-2">
                    <span class="text-slate-300">Task Success Rate</span>
                    <span class="font-semibold text-emerald-300">{{ completionRate }}%</span>
                  </div>
                  <div class="flex items-center justify-between rounded-lg bg-black/20 px-3 py-2">
                    <span class="text-slate-300">Failure Rate</span>
                    <span class="font-semibold text-rose-300">{{ failureRate }}%</span>
                  </div>
                  <div class="flex items-center justify-between rounded-lg bg-black/20 px-3 py-2">
                    <span class="text-slate-300">Platform Status</span>
                    <span class="inline-flex items-center gap-1.5 font-semibold" :class="appSettings?.maintenance_mode ? 'text-amber-300' : 'text-emerald-300'">
                      <span class="h-1.5 w-1.5 rounded-full" :class="appSettings?.maintenance_mode ? 'bg-amber-300' : 'bg-emerald-300'"></span>
                      {{ appSettings?.maintenance_mode ? 'Maintenance' : 'Healthy' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="relative overflow-hidden rounded-[28px] border border-slate-100 bg-gradient-to-br from-[#eef2ff] to-white p-5 shadow-sm">
            <div class="pointer-events-none absolute -top-10 -right-10 h-40 w-40 rounded-full bg-[#6366f1]/10 blur-3xl"></div>
            <div class="relative flex flex-wrap items-center justify-between gap-6">
              <div class="flex items-center gap-4">
                <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/25">
                  <svg class="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                  </svg>
                </div>
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-[#4f46e5]">Geospatial Coverage</p>
                  <p class="mt-1 text-3xl font-black tracking-tight text-slate-900">{{ formattedCoverage }} <span class="text-base font-bold text-slate-400">km²</span></p>
                  <p class="mt-1 text-xs text-slate-500">Total area analyzed across every AOI on the platform.</p>
                </div>
              </div>
              <div class="rounded-2xl border border-slate-100 bg-white/70 px-5 py-3 text-center">
                <p class="text-2xl font-black text-slate-900">{{ dashboard?.distinct_regions ?? '—' }}</p>
                <p class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Regions Monitored</p>
              </div>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="card in dashboardCards"
              :key="card.label"
              class="group rounded-3xl border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div class="flex items-center justify-between">
                <p class="text-sm text-slate-500">{{ card.label }}</p>
                <div class="flex h-10 w-10 items-center justify-center rounded-2xl text-lg transition group-hover:scale-105" :class="card.iconBg">
                  {{ card.icon }}
                </div>
              </div>
              <h3 class="mt-3 text-3xl font-black tracking-tight text-slate-900">{{ card.value }}</h3>
            </article>
          </div>

          <div class="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Task Health</h2>
              <p class="mt-1 text-sm text-slate-500">Running vs failed analyses across the whole platform.</p>
              <div class="mt-4 h-56">
                <Bar v-if="taskHealthChart" :data="taskHealthChart" :options="barOptions" />
              </div>
            </div>

            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Operational Insights</h2>
              <p class="mt-1 text-sm text-slate-500">Fast health checks for immediate admin decisions.</p>

              <div class="mt-4 space-y-3">
                <div class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
                  <span class="text-xs font-semibold text-slate-600">Completed Analyses</span>
                  <span class="text-sm font-bold text-slate-900">{{ completedTasks }}</span>
                </div>
                <div class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
                  <span class="text-xs font-semibold text-slate-600">Success Ratio</span>
                  <span class="text-sm font-bold text-emerald-600">{{ completionRate }}%</span>
                </div>
                <div class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
                  <span class="text-xs font-semibold text-slate-600">Failure Ratio</span>
                  <span class="text-sm font-bold text-rose-600">{{ failureRate }}%</span>
                </div>
                <div class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
                  <span class="text-xs font-semibold text-slate-600">Current Version</span>
                  <span class="text-sm font-bold text-slate-900">v{{ appSettings?.version || '1.0.0' }}</span>
                </div>
              </div>

              <button class="mt-4 w-full rounded-xl bg-[#6366f1] px-3 py-2 text-xs font-semibold text-white transition hover:bg-[#5558e6]" @click="activeTab = 'Settings'">
                Open System Settings
              </button>
            </div>
          </div>

          <div class="grid gap-6 xl:grid-cols-2">
            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Platform Volume</h2>
              <p class="mt-1 text-sm text-slate-500">Projects, analyses, and exports at a glance.</p>
              <div class="mt-4 h-64">
                <Bar v-if="volumeChart" :data="volumeChart" :options="barOptions" />
              </div>
            </div>

            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Analysis Outcomes</h2>
              <p class="mt-1 text-sm text-slate-500">Completed vs running vs failed tasks.</p>
              <div class="mt-4 flex h-64 items-center justify-center">
                <Doughnut v-if="outcomeChart" :data="outcomeChart" :options="pieOptions" />
              </div>
            </div>
          </div>
        </div>

        <!-- Users -->
        <div v-if="activeTab === 'Users'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">👥 Users Management</h2>
              <p class="text-sm text-slate-500">{{ filteredUsers.length }} of {{ users.length }} accounts</p>
            </div>
            <div class="flex items-center gap-2">
              <label class="relative">
                <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="7" />
                  <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
                </svg>
                <input v-model="userSearch" type="text" placeholder="Search users…" class="w-52 rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#6366f1]" />
              </label>
              <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openUserModal()">
                + New User
              </button>
            </div>
          </div>

          <p v-if="usersError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ usersError }}</p>

          <div class="overflow-hidden rounded-[22px] border border-slate-100">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 font-medium">Name</th>
                  <th class="px-4 py-3 font-medium">Email</th>
                  <th class="px-4 py-3 font-medium">Role</th>
                  <th class="px-4 py-3 font-medium">Status</th>
                  <th class="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in filteredUsers" :key="u.id" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-3">
                      <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white" :class="u.role === 'Admin' ? 'bg-amber-500' : 'bg-[#6366f1]'">
                        {{ initials(u.full_name) }}
                      </div>
                      <span class="font-medium text-slate-800">{{ u.full_name }}</span>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-slate-500">{{ u.email }}</td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold" :class="u.role === 'Admin' ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'">
                      {{ u.role === 'Admin' ? '👑 Admin' : '👤 User' }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="u.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'">
                      <span class="h-1.5 w-1.5 rounded-full" :class="u.is_active ? 'bg-emerald-500' : 'bg-slate-400'"></span>
                      {{ u.is_active ? 'Active' : 'Disabled' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <button class="mr-2 text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5]" @click="openUserModal(u)">Edit</button>
                    <button class="text-xs font-semibold text-rose-500 hover:text-rose-600" @click="deleteUser(u)">Delete</button>
                  </td>
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="5" class="px-4 py-10 text-center text-sm text-slate-400">No users match "{{ userSearch }}".</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Datasets -->
        <div v-if="activeTab === 'Datasets'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-bold text-slate-900">🛰️ Datasets Management</h2>
              <p class="text-sm text-slate-500">{{ datasets.length }} datasets</p>
            </div>
            <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openDatasetModal()">
              + New Dataset
            </button>
          </div>

          <p v-if="datasetsError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ datasetsError }}</p>

          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <article v-for="d in datasets" :key="d.id" class="group rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <div class="flex items-start justify-between gap-2">
                <p class="text-sm font-bold text-slate-900">{{ d.name }}</p>
                <span class="whitespace-nowrap rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide" :class="providerBadge(d.provider)">{{ d.provider }}</span>
              </div>
              <p class="mt-2 text-xs font-semibold text-slate-500">{{ d.category }} · {{ d.resolution || '—' }}</p>
              <p class="mt-1.5 truncate rounded-lg bg-slate-50 px-2 py-1 font-mono text-[11px] text-slate-400" :title="d.gee_collection">{{ d.gee_collection }}</p>
              <div class="mt-3 flex gap-3 border-t border-slate-100 pt-3">
                <button class="text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5]" @click="openDatasetModal(d)">Edit</button>
                <button class="text-xs font-semibold text-rose-500 hover:text-rose-600" @click="deleteDataset(d)">Delete</button>
              </div>
            </article>
            <p v-if="datasets.length === 0" class="col-span-full py-10 text-center text-sm text-slate-400">No datasets yet.</p>
          </div>
        </div>

        <!-- Indicators -->
        <div v-if="activeTab === 'Indicators'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <div>
              <h2 class="text-lg font-bold text-slate-900">📊 Indicators Management</h2>
              <p class="text-sm text-slate-500">{{ indicators.length }} indicators</p>
            </div>
            <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="openIndicatorModal()">
              + New Indicator
            </button>
          </div>

          <p v-if="indicatorsError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ indicatorsError }}</p>

          <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <article v-for="i in indicators" :key="i.id" class="group rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
              <div class="flex items-center gap-2.5">
                <div class="flex h-9 w-9 items-center justify-center rounded-xl text-base" :style="{ backgroundColor: (i.color || '#6366f1') + '1a' }">
                  {{ i.icon || '📊' }}
                </div>
                <div>
                  <p class="text-sm font-bold text-slate-900">{{ i.name }}</p>
                  <p class="text-xs font-semibold text-slate-500">{{ i.category }}</p>
                </div>
              </div>
              <p v-if="i.formula" class="mt-2.5 truncate rounded-lg bg-slate-50 px-2 py-1 font-mono text-[11px] text-slate-400" :title="i.formula">{{ i.formula }}</p>
              <div class="mt-3 flex gap-3 border-t border-slate-100 pt-3">
                <button class="text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5]" @click="openIndicatorModal(i)">Edit</button>
                <button class="text-xs font-semibold text-rose-500 hover:text-rose-600" @click="deleteIndicator(i)">Delete</button>
              </div>
            </article>
            <p v-if="indicators.length === 0" class="col-span-full py-10 text-center text-sm text-slate-400">No indicators yet.</p>
          </div>
        </div>

        <!-- Global Statistics -->
        <div v-if="activeTab === 'Statistics'" class="space-y-6">
          <div class="relative overflow-hidden rounded-[28px] border border-slate-200 bg-slate-900 p-6 text-white shadow-sm">
            <div class="pointer-events-none absolute -top-16 -left-10 h-48 w-48 rounded-full bg-[#6366f1]/25 blur-3xl"></div>
            <div class="pointer-events-none absolute -bottom-20 right-0 h-52 w-52 rounded-full bg-cyan-400/20 blur-3xl"></div>

            <div class="relative grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
              <div>
                <p class="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-300">Statistics Center</p>
                <h2 class="mt-2 text-2xl font-black tracking-tight">Platform Intelligence Snapshot</h2>
                <p class="mt-2 max-w-2xl text-sm text-slate-300">Deep visibility into operational load, data coverage, and user activity across the platform.</p>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <div class="rounded-xl bg-white/10 px-3 py-2.5">
                  <p class="text-[10px] uppercase tracking-wider text-slate-300">Active Users</p>
                  <p class="mt-1 text-lg font-black">{{ activeUsersCount }}</p>
                </div>
                <div class="rounded-xl bg-white/10 px-3 py-2.5">
                  <p class="text-[10px] uppercase tracking-wider text-slate-300">Admins</p>
                  <p class="mt-1 text-lg font-black">{{ adminUsersCount }}</p>
                </div>
                <div class="rounded-xl bg-white/10 px-3 py-2.5">
                  <p class="text-[10px] uppercase tracking-wider text-slate-300">Data Sources</p>
                  <p class="mt-1 text-lg font-black">{{ datasetProvidersCount }}</p>
                </div>
                <div class="rounded-xl bg-white/10 px-3 py-2.5">
                  <p class="text-[10px] uppercase tracking-wider text-slate-300">Open Issues</p>
                  <p class="mt-1 text-lg font-black">{{ taskBacklog }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <article v-for="card in dashboardCards" :key="card.label" class="rounded-3xl border border-slate-100 bg-white p-5 shadow-sm">
              <div class="flex items-center justify-between">
                <p class="text-sm text-slate-500">{{ card.label }}</p>
                <div class="flex h-9 w-9 items-center justify-center rounded-xl text-base" :class="card.iconBg">{{ card.icon }}</div>
              </div>
              <p class="mt-2 text-2xl font-black text-slate-900">{{ card.value }}</p>
            </article>
          </div>

          <div class="grid gap-6 xl:grid-cols-[1fr_1fr]">
            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Platform Volume</h2>
              <p class="mt-1 text-sm text-slate-500">Projects, analyses, and exports at a glance.</p>
              <div class="mt-4 h-64">
                <Bar v-if="volumeChart" :data="volumeChart" :options="barOptions" />
              </div>
            </div>
            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
              <h2 class="text-lg font-bold text-slate-900">Analysis Outcomes</h2>
              <p class="mt-1 text-sm text-slate-500">Running vs failed vs completed tasks.</p>
              <div class="mt-4 flex h-64 items-center justify-center">
                <Doughnut v-if="outcomeChart" :data="outcomeChart" :options="pieOptions" />
              </div>
            </div>

            <div class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm xl:col-span-2">
              <div class="flex items-center justify-between">
                <div>
                  <h2 class="text-lg font-bold text-slate-900">Dataset Provider Mix</h2>
                  <p class="mt-1 text-sm text-slate-500">Distribution of configured datasets by provider.</p>
                </div>
                <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">{{ datasets.length }} datasets</span>
              </div>

              <div class="mt-4 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
                <div class="flex h-64 items-center justify-center rounded-2xl bg-slate-50/70">
                  <Doughnut v-if="providerDistributionChart" :data="providerDistributionChart" :options="pieOptions" />
                  <p v-else class="text-sm text-slate-400">No dataset distribution available.</p>
                </div>
                <div class="space-y-2">
                  <div v-for="row in providerBreakdown" :key="row.name" class="flex items-center justify-between rounded-xl border border-slate-100 px-3 py-2.5">
                    <div class="flex items-center gap-2">
                      <span class="h-2.5 w-2.5 rounded-full" :style="{ backgroundColor: row.color }"></span>
                      <span class="text-sm font-semibold text-slate-700">{{ row.name }}</span>
                    </div>
                    <span class="text-sm font-bold text-slate-900">{{ row.count }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- All Projects -->
        <div v-if="activeTab === 'Projects'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">📁 All Projects</h2>
              <p class="text-sm text-slate-500">{{ filteredProjects.length }} of {{ allProjects.length }} projects across every user.</p>
            </div>
            <label class="relative">
              <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="7" />
                <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input v-model="projectSearch" type="text" placeholder="Search projects…" class="w-52 rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#6366f1]" />
            </label>
          </div>

          <div class="overflow-hidden rounded-[22px] border border-slate-100">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 font-medium">Name</th>
                  <th class="px-4 py-3 font-medium">Owner</th>
                  <th class="px-4 py-3 font-medium">Status</th>
                  <th class="px-4 py-3 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredProjects" :key="p.id" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                  <td class="px-4 py-3 font-medium text-slate-800">{{ p.name }}</td>
                  <td class="px-4 py-3">
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">User #{{ p.user_id }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(p.status)">
                      <span class="h-1.5 w-1.5 rounded-full" :class="statusDotClass(p.status)"></span>
                      {{ p.status }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-slate-500">{{ formatDate(p.created_at) }}</td>
                </tr>
                <tr v-if="filteredProjects.length === 0">
                  <td colspan="4" class="px-4 py-10 text-center text-sm text-slate-400">No projects match "{{ projectSearch }}".</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Analysis Monitoring -->
        <div v-if="activeTab === 'Analyses'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">🛰️ Analysis Monitoring</h2>
              <p class="text-sm text-slate-500">{{ filteredAnalyses.length }} of {{ allAnalyses.length }} analyses across every user.</p>
            </div>
            <label class="relative">
              <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="7" />
                <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input v-model="analysisSearch" type="text" placeholder="Search analyses…" class="w-52 rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#6366f1]" />
            </label>
          </div>

          <p v-if="analysesError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ analysesError }}</p>

          <div class="overflow-hidden rounded-[22px] border border-slate-100">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 font-medium">Name</th>
                  <th class="px-4 py-3 font-medium">Owner</th>
                  <th class="px-4 py-3 font-medium">Indicator</th>
                  <th class="px-4 py-3 font-medium">Status</th>
                  <th class="px-4 py-3 font-medium">Created</th>
                  <th class="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in filteredAnalyses" :key="a.id" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                  <td class="px-4 py-3 font-medium text-slate-800">{{ a.name }}</td>
                  <td class="px-4 py-3">
                    <span class="text-slate-700">{{ a.owner || '—' }}</span>
                    <span class="block text-xs text-slate-400">{{ a.owner_email }}</span>
                  </td>
                  <td class="px-4 py-3 text-slate-500">{{ a.indicator || '—' }}</td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(a.status)">
                      <span class="h-1.5 w-1.5 rounded-full" :class="statusDotClass(a.status)"></span>
                      {{ a.status }}
                    </span>
                    <p v-if="a.error_message" class="mt-1 max-w-xs truncate text-[11px] text-rose-500" :title="a.error_message">{{ a.error_message }}</p>
                  </td>
                  <td class="px-4 py-3 text-slate-500">{{ formatDate(a.created_at) }}</td>
                  <td class="px-4 py-3 text-right whitespace-nowrap">
                    <button
                      v-if="a.status === 'Failed'"
                      class="mr-3 text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5] disabled:opacity-50"
                      :disabled="analysisActionId === a.id"
                      @click="retryAnalysis(a)"
                    >
                      {{ analysisActionId === a.id ? 'Retrying…' : 'Retry' }}
                    </button>
                    <button
                      v-if="a.status === 'Running'"
                      class="mr-3 text-xs font-semibold text-amber-600 hover:text-amber-700 disabled:opacity-50"
                      :disabled="analysisActionId === a.id"
                      @click="cancelAnalysis(a)"
                    >
                      Cancel
                    </button>
                    <button class="text-xs font-semibold text-rose-500 hover:text-rose-600" @click="deleteAnalysis(a)">Delete</button>
                  </td>
                </tr>
                <tr v-if="filteredAnalyses.length === 0">
                  <td colspan="6" class="px-4 py-10 text-center text-sm text-slate-400">No analyses match "{{ analysisSearch }}".</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Export Monitoring -->
        <div v-if="activeTab === 'Exports'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">📤 Export Monitoring</h2>
              <p class="text-sm text-slate-500">{{ filteredExports.length }} of {{ allExports.length }} exports across every user.</p>
            </div>
            <label class="relative">
              <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="7" />
                <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input v-model="exportSearch" type="text" placeholder="Search exports…" class="w-52 rounded-xl border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-[#6366f1]" />
            </label>
          </div>

          <p v-if="exportsError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ exportsError }}</p>

          <div class="overflow-hidden rounded-[22px] border border-slate-100">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 font-medium">File</th>
                  <th class="px-4 py-3 font-medium">Owner</th>
                  <th class="px-4 py-3 font-medium">Analysis</th>
                  <th class="px-4 py-3 font-medium">Type</th>
                  <th class="px-4 py-3 font-medium">Status</th>
                  <th class="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in filteredExports" :key="e.id" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                  <td class="px-4 py-3 font-medium text-slate-800">{{ e.file_name }}</td>
                  <td class="px-4 py-3">
                    <span class="text-slate-700">{{ e.owner || '—' }}</span>
                    <span class="block text-xs text-slate-400">{{ e.owner_email }}</span>
                  </td>
                  <td class="px-4 py-3 text-slate-500">{{ e.analysis || '—' }}</td>
                  <td class="px-4 py-3">
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">{{ e.type }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="statusClass(e.status)">
                      <span class="h-1.5 w-1.5 rounded-full" :class="statusDotClass(e.status)"></span>
                      {{ e.status }}
                    </span>
                    <p v-if="e.error_message" class="mt-1 max-w-xs truncate text-[11px] text-rose-500" :title="e.error_message">{{ e.error_message }}</p>
                  </td>
                  <td class="px-4 py-3 text-right whitespace-nowrap">
                    <button
                      v-if="e.status === 'Failed'"
                      class="mr-3 text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5] disabled:opacity-50"
                      :disabled="exportActionId === e.id"
                      @click="retryExport(e)"
                    >
                      {{ exportActionId === e.id ? 'Retrying…' : 'Retry' }}
                    </button>
                    <button class="text-xs font-semibold text-rose-500 hover:text-rose-600" @click="deleteExportAdmin(e)">Delete</button>
                  </td>
                </tr>
                <tr v-if="filteredExports.length === 0">
                  <td colspan="6" class="px-4 py-10 text-center text-sm text-slate-400">No exports match "{{ exportSearch }}".</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- System Logs -->
        <div v-if="activeTab === 'Logs'" class="rounded-[28px] border border-slate-100 bg-white p-5 shadow-sm">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">📜 System Logs</h2>
              <p class="text-sm text-slate-500">Latest {{ logs.length }} platform events.</p>
            </div>
            <div class="flex items-center gap-2">
              <select v-model="logActionFilter" class="rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" @change="loadLogs">
                <option value="">All actions</option>
                <option v-for="a in logActionOptions" :key="a" :value="a">{{ a }}</option>
              </select>
              <button class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50" @click="loadLogs">Refresh</button>
            </div>
          </div>

          <p v-if="logsError" class="mb-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ logsError }}</p>

          <div class="overflow-hidden rounded-[22px] border border-slate-100">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 font-medium">Action</th>
                  <th class="px-4 py-3 font-medium">User</th>
                  <th class="px-4 py-3 font-medium">Details</th>
                  <th class="px-4 py-3 font-medium">When</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in logs" :key="log.id" class="border-t border-slate-100 transition hover:bg-slate-50/80">
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold" :class="logBadge(log.action)">{{ log.action }}</span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-slate-700">{{ log.user || 'System' }}</span>
                    <span v-if="log.user_email" class="block text-xs text-slate-400">{{ log.user_email }}</span>
                  </td>
                  <td class="px-4 py-3 max-w-sm truncate text-slate-500" :title="log.details">{{ log.details || '—' }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-slate-500">{{ formatDateTime(log.created_at) }}</td>
                </tr>
                <tr v-if="logs.length === 0">
                  <td colspan="4" class="px-4 py-10 text-center text-sm text-slate-400">No log entries yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- System Settings -->
        <div v-if="activeTab === 'Settings'" class="max-w-xl rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
          <div class="flex items-center gap-3">
            <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#eef2ff] text-xl">⚙️</div>
            <div>
              <h2 class="text-lg font-bold text-slate-900">System Settings</h2>
              <p class="text-xs text-slate-500">Global application configuration.</p>
            </div>
          </div>

          <p v-if="settingsSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Settings saved.</p>
          <p v-if="settingsError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ settingsError }}</p>

          <div v-if="appSettings" class="mt-5 space-y-4">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Application Name</span>
              <input v-model="appSettings.app_name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Version</span>
              <input v-model="appSettings.version" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
            </label>

            <div class="flex items-center justify-between rounded-2xl border border-slate-100 bg-slate-50/70 px-4 py-3">
              <div>
                <p class="text-sm font-semibold text-slate-800">Maintenance Mode</p>
                <p class="text-xs text-slate-500">Temporarily block non-admin access to the platform.</p>
              </div>
              <button
                type="button"
                class="relative h-6 w-11 shrink-0 rounded-full transition"
                :class="appSettings.maintenance_mode ? 'bg-[#6366f1]' : 'bg-slate-300'"
                @click="appSettings.maintenance_mode = !appSettings.maintenance_mode"
              >
                <span class="absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform" :class="appSettings.maintenance_mode ? 'translate-x-5' : 'translate-x-0.5'"></span>
              </button>
            </div>
          </div>

          <button
            class="mt-6 rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
            :disabled="isSavingSettings"
            @click="saveSettings()"
          >
            {{ isSavingSettings ? 'Saving…' : 'Save Settings' }}
          </button>
        </div>
      </template>
    </section>

    <!-- User modal -->
    <div v-if="showUserModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="showUserModal = false">
      <div class="w-full max-w-sm rounded-[28px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">{{ editingUserId ? 'Edit User' : 'New User' }}</h3>
        <p v-if="userModalError" class="mt-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ userModalError }}</p>
        <div class="mt-4 space-y-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Full Name</span>
            <input v-model="userForm.full_name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Email</span>
            <input v-model="userForm.email" type="email" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label v-if="!editingUserId" class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Password</span>
            <input v-model="userForm.password" type="password" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Role</span>
            <select v-model="userForm.role" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]">
              <option value="User">User</option>
              <option value="Admin">Admin</option>
            </select>
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="showUserModal = false">Cancel</button>
          <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="saveUser()">Save</button>
        </div>
      </div>
    </div>

    <!-- Dataset modal -->
    <div v-if="showDatasetModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="showDatasetModal = false">
      <div class="w-full max-w-sm rounded-[28px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">{{ editingDatasetId ? 'Edit Dataset' : 'New Dataset' }}</h3>
        <p v-if="datasetModalError" class="mt-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ datasetModalError }}</p>
        <div class="mt-4 space-y-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Name</span>
            <input v-model="datasetForm.name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Provider</span>
            <select v-model="datasetForm.provider" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]">
              <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">GEE Collection ID</span>
            <input v-model="datasetForm.gee_collection" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" placeholder="e.g. COPERNICUS/S2_SR_HARMONIZED" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Category</span>
            <select v-model="datasetForm.category" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]">
              <option v-for="c in datasetCategories" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Resolution</span>
            <input v-model="datasetForm.resolution" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" placeholder="e.g. 10 m" />
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="showDatasetModal = false">Cancel</button>
          <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="saveDataset()">Save</button>
        </div>
      </div>
    </div>

    <!-- Indicator modal -->
    <div v-if="showIndicatorModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="showIndicatorModal = false">
      <div class="w-full max-w-sm rounded-[28px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-slate-900">{{ editingIndicatorId ? 'Edit Indicator' : 'New Indicator' }}</h3>
        <p v-if="indicatorModalError" class="mt-3 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ indicatorModalError }}</p>
        <div class="mt-4 space-y-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Name</span>
            <input v-model="indicatorForm.name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Category</span>
            <select v-model="indicatorForm.category" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]">
              <option v-for="c in indicatorCategories" :key="c" :value="c">{{ c }}</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Icon (emoji)</span>
            <input v-model="indicatorForm.icon" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" placeholder="🌿" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Formula</span>
            <input v-model="indicatorForm.formula" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Description</span>
            <textarea v-model="indicatorForm.description" rows="2" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm outline-none focus:border-[#6366f1]"></textarea>
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-50" @click="showIndicatorModal = false">Cancel</button>
          <button class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6]" @click="saveIndicator()">Save</button>
        </div>
      </div>
    </div>
  </AdminShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut } from 'vue-chartjs'
import { Chart, BarElement, BarController, ArcElement, PieController, DoughnutController, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import AdminShell from '@/components/Layout/AdminShell.vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

Chart.register(BarElement, BarController, ArcElement, PieController, DoughnutController, CategoryScale, LinearScale, Tooltip, Legend)

const auth = useAuthStore()

const activeTab = ref('Dashboard')

const dashboard = ref(null)
const users = ref([])
const datasets = ref([])
const indicators = ref([])
const allProjects = ref([])
const appSettings = ref(null)
const allAnalyses = ref([])
const allExports = ref([])
const logs = ref([])

const usersError = ref('')
const datasetsError = ref('')
const indicatorsError = ref('')
const settingsError = ref('')
const settingsSuccess = ref(false)
const isSavingSettings = ref(false)
const analysesError = ref('')
const exportsError = ref('')
const logsError = ref('')

const providers = ['Sentinel-2', 'Landsat-8', 'MODIS', 'CHIRPS', 'WorldPop']
const datasetCategories = ['Vegetation', 'Climate', 'Elevation', 'Population', 'Land Cover', 'Water', 'Urban']
const indicatorCategories = ['Vegetation', 'Water', 'Temperature', 'Climate', 'Land Cover', 'Urban', 'Population', 'Land Degradation', 'Risk']

const formattedCoverage = computed(() => {
  const value = dashboard.value?.total_coverage_km2
  if (typeof value !== 'number') return '—'
  return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
})

const dashboardCards = computed(() => {
  const d = dashboard.value
  if (!d) return []
  return [
    { label: 'Total Users', value: d.total_users, icon: '👥', iconBg: 'bg-[#eef2ff]' },
    { label: 'Total Projects', value: d.total_projects, icon: '📁', iconBg: 'bg-sky-50' },
    { label: 'Total Analyses', value: d.total_analyses, icon: '🛰️', iconBg: 'bg-violet-50' },
    { label: 'Total Exports', value: d.total_exports, icon: '📤', iconBg: 'bg-emerald-50' },
    { label: 'Running Tasks', value: d.running_tasks, icon: '⏳', iconBg: 'bg-amber-50' },
    { label: 'Failed Tasks', value: d.failed_tasks, icon: '⚠️', iconBg: 'bg-rose-50' },
  ]
})

const taskHealthChart = computed(() => {
  const d = dashboard.value
  if (!d) return null
  return {
    labels: ['Running', 'Failed'],
    datasets: [{ data: [d.running_tasks, d.failed_tasks], backgroundColor: ['#f59e0b', '#ef4444'], borderRadius: 8 }],
  }
})

const volumeChart = computed(() => {
  const d = dashboard.value
  if (!d) return null
  return {
    labels: ['Projects', 'Analyses', 'Exports'],
    datasets: [{ data: [d.total_projects, d.total_analyses, d.total_exports], backgroundColor: ['#0ea5e9', '#8b5cf6', '#22c55e'], borderRadius: 8 }],
  }
})

const outcomeChart = computed(() => {
  const d = dashboard.value
  if (!d) return null
  const completed = Math.max(d.total_analyses - d.running_tasks - d.failed_tasks, 0)
  return {
    labels: ['Completed', 'Running', 'Failed'],
    datasets: [{ data: [completed, d.running_tasks, d.failed_tasks], backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'] }],
  }
})

const completedTasks = computed(() => {
  const d = dashboard.value
  if (!d) return 0
  return Math.max(d.total_analyses - d.running_tasks - d.failed_tasks, 0)
})

const completionRate = computed(() => {
  const d = dashboard.value
  if (!d || d.total_analyses === 0) return 0
  return Math.round((completedTasks.value / d.total_analyses) * 100)
})

const failureRate = computed(() => {
  const d = dashboard.value
  if (!d || d.total_analyses === 0) return 0
  return Math.round((d.failed_tasks / d.total_analyses) * 100)
})

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-GB', {
    weekday: 'long',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }),
)

const activeUsersCount = computed(() => users.value.filter((u) => u.is_active).length)
const adminUsersCount = computed(() => users.value.filter((u) => u.role === 'Admin').length)
const datasetProvidersCount = computed(() => new Set(datasets.value.map((d) => d.provider).filter(Boolean)).size)
const taskBacklog = computed(() => {
  const d = dashboard.value
  if (!d) return 0
  return d.running_tasks + d.failed_tasks
})

const PROVIDER_COLORS = {
  'Sentinel-2': '#0ea5e9',
  'Landsat-8': '#22c55e',
  MODIS: '#f43f5e',
  CHIRPS: '#6366f1',
  WorldPop: '#f59e0b',
}

const providerBreakdown = computed(() => {
  const grouped = datasets.value.reduce((acc, dataset) => {
    const key = dataset.provider || 'Other'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})

  return Object.entries(grouped)
    .map(([name, count]) => ({
      name,
      count,
      color: PROVIDER_COLORS[name] || '#94a3b8',
    }))
    .sort((a, b) => b.count - a.count)
})

const providerDistributionChart = computed(() => {
  if (!providerBreakdown.value.length) return null
  return {
    labels: providerBreakdown.value.map((row) => row.name),
    datasets: [
      {
        data: providerBreakdown.value.map((row) => row.count),
        backgroundColor: providerBreakdown.value.map((row) => row.color),
      },
    ],
  }
})

const barOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
const pieOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }

async function loadAll() {
  await auth.load()
  if (!auth.isAdmin) return
  try {
    const [dashRes, usersRes, datasetsRes, indicatorsRes, projectsRes, settingsRes, analysesRes, exportsRes] = await Promise.all([
      api.get('admin/dashboard'),
      api.get('admin/users'),
      api.get('datasets'),
      api.get('indicators'),
      api.get('admin/projects'),
      api.get('admin/settings'),
      api.get('admin/analyses'),
      api.get('admin/exports'),
    ])
    dashboard.value = dashRes.data
    users.value = usersRes.data
    datasets.value = datasetsRes.data
    indicators.value = indicatorsRes.data
    allProjects.value = projectsRes.data
    appSettings.value = settingsRes.data
    allAnalyses.value = analysesRes.data
    allExports.value = exportsRes.data
  } catch (error) {
    usersError.value = error.response?.data?.detail || 'Unable to load admin data.'
  }
  loadLogs()
}

onMounted(loadAll)

// ---- Analysis Monitoring ----
const analysisSearch = ref('')
const analysisActionId = ref(null)
const filteredAnalyses = computed(() => {
  const q = analysisSearch.value.trim().toLowerCase()
  if (!q) return allAnalyses.value
  return allAnalyses.value.filter(
    (a) => a.name.toLowerCase().includes(q) || (a.owner || '').toLowerCase().includes(q) || (a.owner_email || '').toLowerCase().includes(q),
  )
})

async function retryAnalysis(analysis) {
  analysisActionId.value = analysis.id
  analysesError.value = ''
  try {
    const { data } = await api.post(`admin/analyses/${analysis.id}/retry`)
    const idx = allAnalyses.value.findIndex((a) => a.id === analysis.id)
    if (idx !== -1) allAnalyses.value[idx] = data
  } catch (error) {
    analysesError.value = error.response?.data?.detail || 'Unable to retry this analysis.'
  } finally {
    analysisActionId.value = null
  }
}

async function cancelAnalysis(analysis) {
  if (!confirm(`Cancel "${analysis.name}"?`)) return
  analysisActionId.value = analysis.id
  analysesError.value = ''
  try {
    const { data } = await api.post(`admin/analyses/${analysis.id}/cancel`)
    const idx = allAnalyses.value.findIndex((a) => a.id === analysis.id)
    if (idx !== -1) allAnalyses.value[idx] = data
  } catch (error) {
    analysesError.value = error.response?.data?.detail || 'Unable to cancel this analysis.'
  } finally {
    analysisActionId.value = null
  }
}

async function deleteAnalysis(analysis) {
  if (!confirm(`Delete "${analysis.name}"? This cannot be undone.`)) return
  try {
    await api.delete(`admin/analyses/${analysis.id}`)
    allAnalyses.value = allAnalyses.value.filter((a) => a.id !== analysis.id)
  } catch (error) {
    analysesError.value = error.response?.data?.detail || 'Unable to delete this analysis.'
  }
}

// ---- Export Monitoring ----
const exportSearch = ref('')
const exportActionId = ref(null)
const filteredExports = computed(() => {
  const q = exportSearch.value.trim().toLowerCase()
  if (!q) return allExports.value
  return allExports.value.filter(
    (e) => e.file_name.toLowerCase().includes(q) || (e.owner || '').toLowerCase().includes(q) || (e.owner_email || '').toLowerCase().includes(q),
  )
})

async function retryExport(exp) {
  exportActionId.value = exp.id
  exportsError.value = ''
  try {
    const { data } = await api.post(`admin/exports/${exp.id}/retry`)
    const idx = allExports.value.findIndex((e) => e.id === exp.id)
    if (idx !== -1) allExports.value[idx] = data
  } catch (error) {
    exportsError.value = error.response?.data?.detail || 'Unable to retry this export.'
  } finally {
    exportActionId.value = null
  }
}

async function deleteExportAdmin(exp) {
  if (!confirm(`Delete "${exp.file_name}"?`)) return
  try {
    await api.delete(`admin/exports/${exp.id}`)
    allExports.value = allExports.value.filter((e) => e.id !== exp.id)
  } catch (error) {
    exportsError.value = error.response?.data?.detail || 'Unable to delete this export.'
  }
}

// ---- System Logs ----
const logActionFilter = ref('')
const logActionOptions = [
  'User Registered',
  'User Login',
  'Analysis Started',
  'Analysis Completed',
  'Analysis Failed',
  'Analysis Cancelled',
  'Analysis Deleted',
  'Export Started',
  'Export Finished',
  'Export Failed',
  'Export Deleted',
]

async function loadLogs() {
  logsError.value = ''
  try {
    const { data } = await api.get('admin/logs', { params: logActionFilter.value ? { action: logActionFilter.value } : {} })
    logs.value = data
  } catch (error) {
    logsError.value = error.response?.data?.detail || 'Unable to load system logs.'
  }
}

const LOG_BADGES = {
  'User Registered': 'bg-sky-50 text-sky-700',
  'User Login': 'bg-sky-50 text-sky-700',
  'Analysis Started': 'bg-amber-50 text-amber-700',
  'Analysis Completed': 'bg-emerald-50 text-emerald-700',
  'Analysis Failed': 'bg-rose-50 text-rose-700',
  'Analysis Cancelled': 'bg-slate-100 text-slate-600',
  'Analysis Deleted': 'bg-slate-100 text-slate-600',
  'Export Started': 'bg-amber-50 text-amber-700',
  'Export Finished': 'bg-emerald-50 text-emerald-700',
  'Export Failed': 'bg-rose-50 text-rose-700',
  'Export Deleted': 'bg-slate-100 text-slate-600',
}
function logBadge(action) {
  return LOG_BADGES[action] || 'bg-indigo-50 text-indigo-700'
}

function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function statusClass(status) {
  if (status === 'Completed') return 'bg-emerald-50 text-emerald-700'
  if (status === 'Running') return 'bg-amber-50 text-amber-700'
  return 'bg-slate-100 text-slate-500'
}

function statusDotClass(status) {
  if (status === 'Completed') return 'bg-emerald-500'
  if (status === 'Running') return 'bg-amber-500'
  return 'bg-slate-400'
}

const userSearch = ref('')
const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter((u) => u.full_name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
})

const projectSearch = ref('')
const filteredProjects = computed(() => {
  const q = projectSearch.value.trim().toLowerCase()
  if (!q) return allProjects.value
  return allProjects.value.filter((p) => p.name.toLowerCase().includes(q))
})

function initials(name) {
  if (!name) return '?'
  return name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase()
}

const PROVIDER_BADGES = {
  'Sentinel-2': 'bg-sky-50 text-sky-700',
  'Landsat-8': 'bg-emerald-50 text-emerald-700',
  MODIS: 'bg-rose-50 text-rose-700',
  CHIRPS: 'bg-indigo-50 text-indigo-700',
  WorldPop: 'bg-amber-50 text-amber-700',
}
function providerBadge(provider) {
  return PROVIDER_BADGES[provider] || 'bg-slate-100 text-slate-600'
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

// ---- Users CRUD ----
const showUserModal = ref(false)
const editingUserId = ref(null)
const userForm = ref({ full_name: '', email: '', password: '', role: 'User' })
const userModalError = ref('')

function openUserModal(user) {
  userModalError.value = ''
  if (user) {
    editingUserId.value = user.id
    userForm.value = { full_name: user.full_name, email: user.email, password: '', role: user.role }
  } else {
    editingUserId.value = null
    userForm.value = { full_name: '', email: '', password: '', role: 'User' }
  }
  showUserModal.value = true
}

async function saveUser() {
  userModalError.value = ''
  try {
    if (editingUserId.value) {
      const { data } = await api.put(`admin/users/${editingUserId.value}`, {
        full_name: userForm.value.full_name,
        email: userForm.value.email,
        role: userForm.value.role,
      })
      const idx = users.value.findIndex((u) => u.id === editingUserId.value)
      if (idx !== -1) users.value[idx] = data
    } else {
      const { data } = await api.post('admin/users', userForm.value)
      users.value.unshift(data)
    }
    showUserModal.value = false
  } catch (error) {
    userModalError.value = error.response?.data?.detail || 'Unable to save this user.'
  }
}

async function deleteUser(user) {
  if (!confirm(`Delete ${user.full_name}?`)) return
  try {
    await api.delete(`admin/users/${user.id}`)
    users.value = users.value.filter((u) => u.id !== user.id)
  } catch (error) {
    usersError.value = error.response?.data?.detail || 'Unable to delete this user.'
  }
}

// ---- Datasets CRUD ----
const showDatasetModal = ref(false)
const editingDatasetId = ref(null)
const datasetForm = ref({ name: '', provider: 'Sentinel-2', gee_collection: '', category: 'Vegetation', resolution: '' })
const datasetModalError = ref('')

function openDatasetModal(dataset) {
  datasetModalError.value = ''
  if (dataset) {
    editingDatasetId.value = dataset.id
    datasetForm.value = { name: dataset.name, provider: dataset.provider, gee_collection: dataset.gee_collection, category: dataset.category, resolution: dataset.resolution || '' }
  } else {
    editingDatasetId.value = null
    datasetForm.value = { name: '', provider: 'Sentinel-2', gee_collection: '', category: 'Vegetation', resolution: '' }
  }
  showDatasetModal.value = true
}

async function saveDataset() {
  datasetModalError.value = ''
  try {
    if (editingDatasetId.value) {
      const { data } = await api.put(`datasets/${editingDatasetId.value}`, datasetForm.value)
      const idx = datasets.value.findIndex((d) => d.id === editingDatasetId.value)
      if (idx !== -1) datasets.value[idx] = data
    } else {
      const { data } = await api.post('datasets', datasetForm.value)
      datasets.value.unshift(data)
    }
    showDatasetModal.value = false
  } catch (error) {
    datasetModalError.value = error.response?.data?.detail || 'Unable to save this dataset.'
  }
}

async function deleteDataset(dataset) {
  if (!confirm(`Delete ${dataset.name}?`)) return
  try {
    await api.delete(`datasets/${dataset.id}`)
    datasets.value = datasets.value.filter((d) => d.id !== dataset.id)
  } catch (error) {
    datasetsError.value = error.response?.data?.detail || 'Unable to delete this dataset.'
  }
}

// ---- Indicators CRUD ----
const showIndicatorModal = ref(false)
const editingIndicatorId = ref(null)
const indicatorForm = ref({ name: '', category: 'Vegetation', icon: '', formula: '', description: '' })
const indicatorModalError = ref('')

function openIndicatorModal(indicator) {
  indicatorModalError.value = ''
  if (indicator) {
    editingIndicatorId.value = indicator.id
    indicatorForm.value = {
      name: indicator.name,
      category: indicator.category,
      icon: indicator.icon || '',
      formula: indicator.formula || '',
      description: indicator.description || '',
    }
  } else {
    editingIndicatorId.value = null
    indicatorForm.value = { name: '', category: 'Vegetation', icon: '', formula: '', description: '' }
  }
  showIndicatorModal.value = true
}

async function saveIndicator() {
  indicatorModalError.value = ''
  try {
    if (editingIndicatorId.value) {
      const { data } = await api.put(`indicators/${editingIndicatorId.value}`, indicatorForm.value)
      const idx = indicators.value.findIndex((i) => i.id === editingIndicatorId.value)
      if (idx !== -1) indicators.value[idx] = data
    } else {
      const { data } = await api.post('indicators', indicatorForm.value)
      indicators.value.unshift(data)
    }
    showIndicatorModal.value = false
  } catch (error) {
    indicatorModalError.value = error.response?.data?.detail || 'Unable to save this indicator.'
  }
}

async function deleteIndicator(indicator) {
  if (!confirm(`Delete ${indicator.name}?`)) return
  try {
    await api.delete(`indicators/${indicator.id}`)
    indicators.value = indicators.value.filter((i) => i.id !== indicator.id)
  } catch (error) {
    indicatorsError.value = error.response?.data?.detail || 'Unable to delete this indicator.'
  }
}

// ---- Settings ----
async function saveSettings() {
  isSavingSettings.value = true
  settingsError.value = ''
  settingsSuccess.value = false
  try {
    const { data } = await api.put('admin/settings', appSettings.value)
    appSettings.value = data
    settingsSuccess.value = true
  } catch (error) {
    settingsError.value = error.response?.data?.detail || 'Unable to save settings.'
  } finally {
    isSavingSettings.value = false
  }
}
</script>
