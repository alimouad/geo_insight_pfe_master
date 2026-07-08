<template>
  <WorkspaceShell
    title="Statistics"
    subtitle="Every analysis gets a statistical summary and a set of charts for interpretation."
  >
    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
      <article v-for="card in metrics" :key="card.label" class="rounded-[24px] border border-white/10 bg-white/5 p-4 shadow-2xl shadow-slate-950/20 backdrop-blur">
        <p class="text-[10px] font-black uppercase tracking-[0.35em] text-slate-400">{{ card.label }}</p>
        <p class="mt-3 text-3xl font-black text-white">{{ card.value }}</p>
      </article>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur">
        <h2 class="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">Charts</h2>
        <div class="mt-4 grid gap-4 md:grid-cols-2">
          <div v-for="chart in charts" :key="chart.title" class="rounded-3xl border border-white/10 bg-slate-950/40 p-4">
            <p class="text-xs font-bold text-slate-300">{{ chart.title }}</p>
            <div class="mt-4 flex h-40 items-end gap-2 rounded-2xl border border-dashed border-white/10 bg-slate-950/50 p-3">
              <div v-for="bar in chart.bars" :key="bar" class="flex-1 rounded-t-2xl bg-gradient-to-t from-cyan-400 to-emerald-300" :style="{ height: bar + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-4 rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-2xl shadow-slate-950/20 backdrop-blur">
        <h2 class="text-sm font-black uppercase tracking-[0.35em] text-cyan-300">Area Breakdown</h2>
        <div v-for="item in breakdown" :key="item.label" class="rounded-3xl border border-white/10 bg-slate-950/40 p-4">
          <div class="flex items-center justify-between text-sm font-semibold text-slate-200">
            <span>{{ item.label }}</span>
            <span>{{ item.value }}%</span>
          </div>
          <div class="mt-3 h-2 rounded-full bg-white/10">
            <div class="h-2 rounded-full bg-cyan-400" :style="{ width: item.value + '%' }"></div>
          </div>
        </div>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'

const metrics = [
  { label: 'Minimum', value: '0.08' },
  { label: 'Maximum', value: '0.91' },
  { label: 'Mean', value: '0.62' },
  { label: 'Median', value: '0.58' },
  { label: 'Std', value: '0.12' },
  { label: 'Samples', value: '2.4M' },
]

const charts = [
  { title: 'Histogram', bars: [20, 45, 65, 100, 85, 55, 32] },
  { title: 'Time Series', bars: [30, 36, 42, 48, 55, 62, 70] },
]

const breakdown = [
  { label: 'Vegetation %', value: 46 },
  { label: 'Water %', value: 12 },
  { label: 'Urban %', value: 21 },
  { label: 'Forest %', value: 64 },
]
</script>