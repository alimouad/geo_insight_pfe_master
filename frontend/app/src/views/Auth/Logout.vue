<template>
  <main class="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-slate-100">
    <section class="w-full max-w-md rounded-[28px] border border-white/10 bg-white/5 p-8 text-center shadow-2xl shadow-slate-950/20 backdrop-blur">
      <p class="text-xs font-black uppercase tracking-[0.35em] text-cyan-300">GeoInsight</p>
      <h1 class="mt-4 text-3xl font-bold">Signing out</h1>
      <p class="mt-2 text-sm text-slate-300">Your session is being cleared.</p>
      <button class="mt-6 rounded-2xl bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300" @click="backToLogin">
        Back to Login
      </button>
    </section>
  </main>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const backToLogin = () => {
  localStorage.removeItem('token')
  router.replace('/login')
}

onMounted(() => {
  backToLogin()
})
</script>