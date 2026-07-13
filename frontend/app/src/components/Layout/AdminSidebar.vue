<template>
  <aside class="relative flex w-60 shrink-0 flex-col justify-between overflow-hidden bg-slate-900 py-6">
    <div class="pointer-events-none absolute -top-24 -left-16 h-56 w-56 rounded-full bg-[#6366f1]/20 blur-3xl"></div>
    <div class="pointer-events-none absolute -bottom-24 -right-10 h-56 w-56 rounded-full bg-cyan-400/10 blur-3xl"></div>

    <svg class="pointer-events-none absolute inset-0 h-full w-full" viewBox="0 0 240 800" preserveAspectRatio="xMidYMid slice" fill="none">
      <g stroke="#818cf8" stroke-width="1.5" opacity="0.14">
        <path d="M-20 140C30 110 70 95 120 105s85 38 135 32 80-30 130-28" />
        <path d="M-30 320C25 290 78 278 130 292s90 44 140 38 78-26 140-14" />
        <path d="M-20 500C34 468 82 452 138 462s88 40 140 32 74-24 132-16" />
        <path d="M-30 660C28 634 76 620 132 628s92 34 142 26 76-20 136-10" />
      </g>
      <g stroke="#22d3ee" stroke-width="1" opacity="0.1">
        <path d="M-20 210C36 186 84 176 136 186s86 30 136 22 78-18 128-10" />
        <path d="M-30 400C28 372 80 360 134 370s88 32 138 24 76-20 132-10" />
        <path d="M-20 580C32 554 82 542 136 552s86 30 136 22 78-18 128-8" />
      </g>
      <circle cx="70" cy="240" r="3" fill="#6366f1" opacity="0.35" />
      <circle cx="170" cy="450" r="3" fill="#22d3ee" opacity="0.3" />
      <circle cx="100" cy="620" r="3" fill="#f59e0b" opacity="0.3" />
    </svg>

    <div class="relative flex flex-col">
      <router-link to="/admin" class="mb-1 flex items-center gap-3 px-5">
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/30">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </span>
        <span>
          <span class="block text-sm font-black tracking-tight text-white">GeoInsight</span>
          <span class="block text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Admin Console</span>
        </span>
      </router-link>

      <div class="px-5 py-3">
        <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-400/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-emerald-300">
          <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          Live
        </span>
      </div>

      <nav class="mt-2 flex flex-col gap-1 px-3">
        <button
          v-for="item in items"
          :key="item.id"
          type="button"
          class="group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-semibold transition-colors"
          :class="modelValue === item.id ? 'bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/20' : 'text-slate-400 hover:bg-white/5 hover:text-slate-100'"
          @click="$emit('update:modelValue', item.id)"
        >
          <svg class="h-4.5 w-4.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
          </svg>
          <span class="truncate">{{ item.label }}</span>
        </button>
      </nav>
    </div>

    <div class="relative flex flex-col gap-3 px-3">
      <router-link
        to="/dashboard"
        class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold text-rose-300 transition-colors hover:bg-rose-500/10"
      >
        <svg class="h-4.5 w-4.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Exit Admin Deck
      </router-link>

      <div class="flex items-center gap-2.5 rounded-xl bg-white/5 px-3 py-2.5">
        <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-400 text-xs font-bold text-slate-900">
          {{ initials }}
        </span>
        <span class="min-w-0">
          <span class="block truncate text-xs font-semibold text-white">{{ auth.user?.full_name || 'Admin' }}</span>
          <span class="block truncate text-[10px] text-slate-400">{{ auth.user?.email }}</span>
        </span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

defineProps({
  modelValue: { type: String, required: true },
})
defineEmits(['update:modelValue'])

const auth = useAuthStore()
onMounted(() => auth.load())

const initials = computed(() => {
  const name = auth.user?.full_name
  if (!name) return '?'
  return name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase()
})

const items = [
  { id: 'Dashboard', label: 'Dashboard', icon: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V16zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V16z' },
  { id: 'Users', label: 'Users', icon: 'M17 20h5v-2a4 4 0 00-3-3.87M9 20H4v-2a4 4 0 013-3.87m6-2.13a4 4 0 10-4-4 4 4 0 004 4zm6 0a4 4 0 10-4-4' },
  { id: 'Projects', label: 'Projects', icon: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z' },
  { id: 'Datasets', label: 'Datasets', icon: 'M4 7c0-1.1 3.6-2 8-2s8 .9 8 2-3.6 2-8 2-8-.9-8-2zm0 0v10c0 1.1 3.6 2 8 2s8-.9 8-2V7M4 12c0 1.1 3.6 2 8 2s8-.9 8-2' },
  { id: 'Indicators', label: 'Indicators', icon: 'M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138z' },
  { id: 'Analyses', label: 'Analysis Monitoring', icon: 'M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { id: 'Exports', label: 'Export Monitoring', icon: 'M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5 5-5M12 15V3' },
  { id: 'Logs', label: 'System Logs', icon: 'M9 17v-2a2 2 0 012-2h2a2 2 0 012 2v2m-9 0h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2zm4-9h6' },
  { id: 'Statistics', label: 'Statistics', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { id: 'Settings', label: 'Settings', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z' },
]
</script>
