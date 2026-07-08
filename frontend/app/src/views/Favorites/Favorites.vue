<template>
  <WorkspaceShell
    title="Favorites"
    subtitle="Saved analyses that the user marked as important for quick reuse."
  >
    <section class="rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur">
      <table class="w-full border-collapse text-left">
        <thead class="border-b border-white/10 text-[10px] font-black uppercase tracking-[0.35em] text-slate-400">
          <tr>
            <th class="py-3 pr-4">Analysis Name</th>
            <th class="py-3 pr-4">Date</th>
            <th class="py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/10 text-sm text-slate-100">
          <tr v-for="item in favorites" :key="item.name">
            <td class="py-4 pr-4 font-semibold">{{ item.name }}</td>
            <td class="py-4 pr-4 text-slate-300">{{ item.date }}</td>
            <td class="py-4 text-right">
              <div class="flex justify-end gap-2">
                <button class="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold text-slate-100 transition hover:bg-white/10">Open</button>
                <button class="rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-2 text-xs font-semibold text-rose-200 transition hover:bg-rose-400/20">Delete</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'

const favorites = [
  { name: 'NDVI Crop Health Morocco', date: '2026-07-04' },
  { name: 'NDWI Flood Watch Niger', date: '2026-07-02' },
  { name: 'Land Cover Atlas 2026', date: '2026-06-30' },
]
</script>