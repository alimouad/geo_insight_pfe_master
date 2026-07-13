<template>
  <div class="min-h-screen w-full bg-[#eef2f6] flex items-center justify-center p-2 font-sans antialiased text-slate-800">
    <div class="w-full h-screen bg-white rounded-3xl shadow-2xl flex overflow-hidden">
      <SideBar />

      <main class="relative flex-1 p-6 flex flex-col h-screen bg-slate-100/70">
        <svg class="pointer-events-none absolute inset-0 h-full w-full" viewBox="0 0 1000 800" preserveAspectRatio="xMidYMid slice" fill="none">
          <g stroke="#6366f1" stroke-width="1.5" opacity="0.05">
            <path d="M-40 120C120 80 220 60 340 78s190 52 310 42 180-42 300-34 190 26 290 6" />
            <path d="M-60 340C110 300 220 284 350 300s200 48 320 38 176-36 300-26 190 22 280 4" />
            <path d="M-40 560C130 520 232 502 356 518s194 46 316 36 178-34 296-24 186 20 276 2" />
          </g>
          <g stroke="#0ea5ff" stroke-width="1" opacity="0.04">
            <path d="M-50 230C110 198 214 184 336 198s192 40 312 30 178-30 298-22 186 18 276 2" />
            <path d="M-40 450C120 416 224 402 348 416s192 42 314 32 178-32 296-22 186 18 274 2" />
          </g>
          <circle cx="860" cy="120" r="3" fill="#6366f1" opacity="0.16" />
          <circle cx="920" cy="420" r="3" fill="#0ea5ff" opacity="0.14" />
          <circle cx="800" cy="640" r="3" fill="#f59e0b" opacity="0.14" />
        </svg>

        <div class="relative z-10 flex h-full flex-col">
          <Header :title="title" :subtitle="subtitle">
            <template #actions>
              <slot name="actions" />
            </template>
          </Header>
          <div class="flex-1 overflow-y-auto pr-1 mt-8">
            <slot />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import SideBar from '@/components/Layout/SideBar.vue'
import Header from './Header.vue';
const { title, subtitle } = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
})
</script>