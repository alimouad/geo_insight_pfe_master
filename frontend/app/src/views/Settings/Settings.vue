<template>
  <WorkspaceShell
    title="Settings"
    subtitle="Control the visual theme, language, map provider, and notifications."
  >
    <section class="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
      <article v-for="group in settings" :key="group.title" class="rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur">
        <h2 class="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">{{ group.title }}</h2>
        <div class="mt-4 space-y-3">
          <div v-for="option in group.options" :key="option" class="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
            <span class="text-sm font-semibold text-slate-100">{{ option }}</span>
            <span class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-300">Toggle</span>
          </div>
        </div>
      </article>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'

const settings = [
  { title: 'Theme', options: ['Dark', 'Light'] },
  { title: 'Language', options: ['English', 'French', 'Arabic'] },
  { title: 'Map', options: ['OSM', 'Satellite', 'Terrain'] },
  { title: 'Notifications', options: ['Enable', 'Disable'] },
]
</script>