<template>
  <div class="min-h-screen w-full bg-[#eef2f6] flex flex-col items-center justify-center p-6 font-sans antialiased">

    <div class="w-full max-w-[440px] bg-white rounded-[32px] shadow-xl shadow-slate-200/60 border border-slate-100 p-8 md:p-10 relative overflow-hidden">

      <div class="absolute -top-24 -right-24 h-48 w-48 rounded-full bg-[#6366f1]/5 blur-2xl pointer-events-none"></div>
      <div class="absolute -bottom-24 -left-24 h-48 w-48 rounded-full bg-emerald-400/5 blur-2xl pointer-events-none"></div>

      <div class="mb-10 flex items-center gap-2.5">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-[#6366f1] text-white shadow-lg shadow-[#6366f1]/20">
          <svg class="h-4.5 w-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <span class="text-lg font-black tracking-tight text-slate-900">GeoInsight</span>
      </div>

      <div class="mb-8">
        <h1 class="text-2xl font-black tracking-tight text-slate-900">Create your account</h1>
        <p class="mt-2 text-sm text-slate-500">Start running no-code geospatial analyses in minutes.</p>
      </div>

      <p v-if="errorMessage" class="mb-5 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">
        {{ errorMessage }}
      </p>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <label class="block">
          <span class="mb-1.5 block text-xs font-semibold text-slate-700">Full name</span>
          <div class="relative">
            <svg class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <input
              v-model="fullName"
              type="text"
              autocomplete="name"
              placeholder="Mouad Baaziz"
              required
              class="w-full rounded-2xl border border-slate-200 bg-slate-50/70 py-3 pl-10 pr-4 text-sm text-slate-800 placeholder-slate-400 outline-none transition focus:border-[#6366f1] focus:bg-white"
            />
          </div>
        </label>

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

        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Password</span>
            <input
              v-model="password"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              required
              minlength="8"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-800 placeholder-slate-400 outline-none transition focus:border-[#6366f1] focus:bg-white"
            />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Confirm</span>
            <input
              v-model="confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="••••••••"
              required
              minlength="8"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50/70 px-4 py-3 text-sm text-slate-800 placeholder-slate-400 outline-none transition focus:border-[#6366f1] focus:bg-white"
            />
          </label>
        </div>

        <label class="flex select-none items-start gap-2 py-1">
          <input
            type="checkbox"
            v-model="acceptTerms"
            required
            class="mt-0.5 h-4 w-4 rounded border-slate-300 text-[#6366f1] focus:ring-[#6366f1]"
          />
          <span class="text-xs font-semibold text-slate-500">I agree to the Terms of Service and Privacy Policy.</span>
        </label>

        <button
          type="submit"
          :disabled="isLoading"
          class="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#6366f1] px-4 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
        >
          <span v-if="isLoading" class="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white"></span>
          <span>{{ isLoading ? 'Creating account…' : 'Create account' }}</span>
        </button>
      </form>

      <p class="mt-8 border-t border-slate-100 pt-6 text-center text-xs font-semibold text-slate-400">
        Already have an account?
        <router-link to="/login" class="ml-1 font-bold text-[#6366f1] hover:text-[#4f46e5]">Sign in</router-link>
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const isLoading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  isLoading.value = true
  try {
    await api.post('auth/register', {
      full_name: fullName.value,
      email: email.value,
      password: password.value,
    })

    router.push('/login')
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Unable to create your account. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
