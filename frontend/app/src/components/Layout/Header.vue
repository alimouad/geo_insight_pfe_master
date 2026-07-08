
<template>
        <header class="flex items-center justify-between gap-6 shrink-0">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#0ea5ff]">GeoInsight</p>
            <h1 class="mt-1 text-2xl font-black text-slate-900 tracking-tight">{{ title }}</h1>
            <p class="text-xs text-slate-400 mt-0.5 max-w-3xl">{{ subtitle }}</p>
          </div>

          <div class="flex items-center gap-3">
            <label class="relative hidden lg:block">
              <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="7" />
                <path stroke-linecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input
                type="text"
                placeholder="Search projects, analyses, layers…"
                class="w-72 rounded-xl border border-slate-100 bg-slate-50/70 py-2 pl-10 pr-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-200 focus:bg-white"
              />
            </label>

            <slot name="actions" />

            <button type="button" class="relative rounded-xl border border-slate-100 bg-white p-2.5 text-slate-500 shadow-sm transition hover:border-slate-200 hover:bg-slate-50 hover:text-slate-700" title="Notifications">
              <svg class="h-4.5 w-4.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.4-1.4A2 2 0 0118 14.2V11a6 6 0 10-12 0v3.2a2 2 0 01-.6 1.4L4 17h5m6 0a3 3 0 11-6 0m6 0H9" />
              </svg>
              <span class="absolute right-2 top-2 h-2 w-2 rounded-full bg-rose-500"></span>
            </button>

            <button type="button" class="rounded-xl border border-slate-100 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-200 hover:bg-slate-50" @click="router.push('/profile')">
              Profile
            </button>
          </div>
        </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const { title, subtitle } = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
})

const router = useRouter()
</script>