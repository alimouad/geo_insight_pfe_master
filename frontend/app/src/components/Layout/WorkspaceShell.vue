<template>
  <div class="min-h-screen w-full bg-[#eef2f6] flex items-center justify-center p-2 font-sans antialiased text-slate-800">
    <div class="w-full h-screen bg-white rounded-3xl shadow-2xl flex overflow-hidden">
      <SideBar />

      <main class="flex-1 p-6 flex flex-col h-[100vh] bg-slate-100/70">
        <Header :title="title" :subtitle="subtitle">
          <template #actions>
            <slot name="actions" />
          </template>
        </Header>
        <div class="flex-1 overflow-y-auto pr-1 mt-8">
          <slot />
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