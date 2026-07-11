<template>
  <AuthShell
    hero-title="Sign in to your spatial command center."
    hero-subtitle="Track regions, monitor analyses, and manage map-driven workflows from one focused workspace."
    title="Welcome back"
    subtitle="Sign in to continue your geospatial workspace."
    :error-message="errorMessage"
  >
    <form @submit.prevent="handleLogin" class="space-y-4">
      <label class="block">
        <span class="mb-1.5 block text-xs font-semibold text-slate-700">Email</span>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.206" />
          </svg>
          <input
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="you@geoinsight.com"
            required
            class="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 outline-none transition focus:border-[#6366f1] focus:bg-white"
          />
        </div>
      </label>

      <label class="block">
        <div class="mb-1.5 flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-700">Password</span>
          <router-link to="/forgot-password" class="text-xs font-semibold text-[#6366f1] hover:text-[#4f46e5]">Forgot password?</router-link>
        </div>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="••••••••"
            required
            class="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 outline-none transition focus:border-[#6366f1] focus:bg-white"
          />
        </div>
      </label>

      <label class="flex select-none items-center gap-2 py-1">
        <input
          type="checkbox"
          v-model="rememberMe"
          class="h-4 w-4 rounded border-slate-300 text-[#6366f1] focus:ring-[#6366f1]"
        />
        <span class="text-xs font-semibold text-slate-500">Keep me signed in</span>
      </label>

      <button
        type="submit"
        :disabled="isLoading"
        class="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#6366f1] px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
      >
        <span v-if="isLoading" class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white"></span>
        <span>{{ isLoading ? 'Signing in…' : 'Sign in' }}</span>
      </button>
    </form>

    <template #footer>
      Don't have an account?
      <router-link to="/register" class="ml-1 font-bold text-[#6366f1] hover:text-[#4f46e5]">Create one</router-link>
    </template>
  </AuthShell>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthShell from '@/components/Layout/AuthShell.vue'
import api from '@/services/api'

const router = useRouter()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  isLoading.value = true
  try {
    const { data } = await api.post('auth/login', {
      email: email.value,
      password: password.value,
    })

    localStorage.setItem('token', data.access_token)
    router.push('/dashboard')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to sign in. Please check your credentials and try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
