<template>
  <div class="min-h-screen w-full overflow-hidden bg-[#eef2f6] font-sans antialiased text-slate-800">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(99,102,241,0.12),transparent_34%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.12),transparent_30%)]"></div>
    <div class="relative min-h-screen grid lg:grid-cols-[1.05fr_0.95fr]">
      <section class="relative hidden items-center px-6 py-10 lg:flex lg:px-12 xl:px-16">
        <div class="pointer-events-none absolute inset-0 opacity-60">
          <div class="absolute left-8 top-12 h-72 w-72 rounded-full bg-[#6366f1]/10 blur-3xl"></div>
          <div class="absolute bottom-10 right-8 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl"></div>
        </div>

        <div class="relative max-w-2xl">
          <div class="mb-8 flex items-center gap-2.5">
            <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/20">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p class="text-[10px] font-black uppercase tracking-[0.34em] text-[#6366f1]">GeoInsight</p>
              <p class="text-sm font-semibold text-slate-500">Maps, layers, and spatial decisions</p>
            </div>
          </div>

          <div class="space-y-5">
            <span class="inline-flex items-center rounded-full border border-[#6366f1]/15 bg-white/70 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.25em] text-[#6366f1] shadow-sm">
              {{ eyebrow }}
            </span>
            <h1 class="max-w-xl text-4xl font-black tracking-tight text-slate-950 md:text-5xl">
              {{ heroTitle }}
            </h1>
            <p class="max-w-xl text-base leading-7 text-slate-600">
              {{ heroSubtitle }}
            </p>
          </div>

          <div class="mt-8 grid gap-3 sm:grid-cols-3">
            <article class="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-sm backdrop-blur">
              <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Coverage</p>
              <p class="mt-2 text-lg font-black text-slate-900">Regional</p>
              <p class="mt-1 text-sm text-slate-500">Zone-aware insight panels</p>
            </article>
            <article class="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-sm backdrop-blur">
              <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Layers</p>
              <p class="mt-2 text-lg font-black text-slate-900">Dynamic</p>
              <p class="mt-1 text-sm text-slate-500">Map data ready to explore</p>
            </article>
            <article class="rounded-3xl border border-white/70 bg-white/80 p-4 shadow-sm backdrop-blur">
              <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">Monitoring</p>
              <p class="mt-2 text-lg font-black text-slate-900">24/7</p>
              <p class="mt-1 text-sm text-slate-500">Continuous geospatial ops</p>
            </article>
          </div>

          <div class="mt-8 rounded-[28px] border border-white/70 bg-white/80 p-5 shadow-xl shadow-slate-200/50 backdrop-blur">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.25em] text-[#6366f1]">Map snapshot</p>
                <p class="mt-1 text-sm text-slate-500">A minimal view of zones, routes, and hotspots.</p>
              </div>
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.2em] text-emerald-700">Live</span>
            </div>

            <div class="mt-4 overflow-hidden rounded-3xl border border-slate-200 bg-[#f8fafc]">
              <svg viewBox="0 0 720 360" class="h-64 w-full">
                <defs>
                  <linearGradient id="terrain" x1="0" x2="1" y1="0" y2="1">
                    <stop offset="0%" stop-color="#e0e7ff" />
                    <stop offset="100%" stop-color="#ecfeff" />
                  </linearGradient>
                </defs>
                <rect width="720" height="360" fill="url(#terrain)" />
                <g fill="none" stroke="#94a3b8" stroke-width="2" opacity="0.45">
                  <path d="M34 252C88 208 126 181 186 186s95 56 155 49 95-48 154-54 109 28 175 18" />
                  <path d="M54 128c51-16 113-11 164 19s97 63 157 60 106-44 166-48 88 18 129 44" />
                  <path d="M42 78c59 31 115 42 178 29s108-54 169-53 103 35 150 54 103 17 167-20" />
                </g>
                <g fill="none" stroke="#cbd5e1" stroke-width="1.5" opacity="0.5">
                  <circle cx="190" cy="116" r="78" />
                  <circle cx="190" cy="116" r="118" />
                  <circle cx="190" cy="116" r="158" />
                </g>
                <path d="M120 268C180 220 228 201 297 198s125 18 183 12 103-39 151-43 91 16 141 44" stroke="#0ea5e9" stroke-width="4" fill="none" opacity="0.9" />
                <circle cx="190" cy="116" r="11" fill="#ef4444" />
                <circle cx="190" cy="116" r="22" fill="#ef4444" opacity="0.18" />
                <circle cx="486" cy="202" r="11" fill="#6366f1" />
                <circle cx="486" cy="202" r="22" fill="#6366f1" opacity="0.18" />
                <circle cx="586" cy="118" r="8" fill="#22c55e" />
                <circle cx="586" cy="118" r="16" fill="#22c55e" opacity="0.18" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      <section class="flex items-center justify-center px-6 py-10 lg:px-10 xl:px-16">
        <div class="relative w-full max-w-[460px] overflow-hidden rounded-[34px] border border-slate-100 bg-white p-8 shadow-2xl shadow-slate-200/70 md:p-10">
          <div class="pointer-events-none absolute -top-20 -right-20 h-48 w-48 rounded-full bg-[#6366f1]/8 blur-3xl"></div>
          <div class="pointer-events-none absolute -bottom-20 -left-16 h-56 w-56 rounded-full bg-cyan-400/8 blur-3xl"></div>

          <div class="mb-6 flex items-center gap-2.5 lg:hidden">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/20">
              <svg class="h-4.5 w-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span class="text-lg font-black tracking-tight text-slate-900">GeoInsight</span>
          </div>

          <div class="mb-8 flex items-center justify-between gap-4">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-[#6366f1]">{{ portalLabel }}</p>
              <h2 class="mt-2 text-2xl font-black tracking-tight text-slate-950">{{ title }}</h2>
            </div>
            <div class="hidden rounded-2xl border border-slate-100 bg-slate-50 px-3 py-2 text-right sm:block">
              <p class="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">Mode</p>
              <p class="text-sm font-bold text-slate-800">Geo workspace</p>
            </div>
          </div>

          <p class="-mt-2 mb-6 text-sm text-slate-500">{{ subtitle }}</p>

          <p v-if="errorMessage" class="mb-5 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">
            {{ errorMessage }}
          </p>

          <slot />

          <p class="mt-8 border-t border-slate-100 pt-6 text-center text-xs font-semibold text-slate-400">
            <slot name="footer" />
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: 'Live geographic intelligence' },
  heroTitle: { type: String, required: true },
  heroSubtitle: { type: String, required: true },
  portalLabel: { type: String, default: 'Access Portal' },
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
  errorMessage: { type: String, default: '' },
})
</script>
