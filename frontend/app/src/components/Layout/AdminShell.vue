<template>
  <div class="min-h-screen w-full bg-[#eef2f6] flex items-center justify-center p-2 font-sans antialiased text-slate-800">
    <div class="w-full h-screen bg-white rounded-3xl shadow-2xl flex overflow-hidden">
      <AdminSidebar :model-value="activeTab" @update:model-value="$emit('update:activeTab', $event)" />

      <main class="flex-1 p-6 flex flex-col h-[100vh] bg-slate-100/70">
        <header class="flex items-center justify-between shrink-0">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#6366f1]">Admin</p>
            <h1 class="mt-1 text-2xl font-black text-slate-900 tracking-tight">{{ title }}</h1>
            <p class="text-xs text-slate-400 mt-0.5 max-w-3xl">{{ subtitle }}</p>
          </div>
          <div class="flex items-center gap-2.5">
            <slot name="actions" />
          </div>
        </header>
        <div class="flex-1 overflow-y-auto pr-1 mt-8">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import AdminSidebar from '@/components/Layout/AdminSidebar.vue'

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
  activeTab: { type: String, required: true },
})
defineEmits(['update:activeTab'])
</script>
