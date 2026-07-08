<template>
  <WorkspaceShell
    title="Profile"
    subtitle="Manage identity and account metadata for the workspace."
  >
    <section v-if="user" class="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
      <div class="rounded-[28px] border border-slate-100 bg-white p-6 text-center shadow-sm">
        <div class="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-[#6366f1] text-4xl font-black text-white">
          {{ initial }}
        </div>
        <h2 class="mt-4 text-2xl font-bold text-slate-900">{{ user.full_name }}</h2>
        <p class="text-sm text-slate-500">{{ user.role }}</p>
        <div class="mt-6 space-y-2 text-left text-sm text-slate-600">
          <p><span class="font-semibold text-slate-500">Email:</span> {{ user.email }}</p>
          <p><span class="font-semibold text-slate-500">Organization:</span> {{ user.organization || '—' }}</p>
          <p><span class="font-semibold text-slate-500">Country:</span> {{ user.country || '—' }}</p>
          <p><span class="font-semibold text-slate-500">Member since:</span> {{ formatDate(user.created_at) }}</p>
        </div>
      </div>

      <div class="space-y-6">
        <div class="rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Edit Profile</h2>

          <p v-if="profileSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Profile updated.</p>
          <p v-if="profileError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ profileError }}</p>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Name</span>
              <input v-model="profileForm.full_name" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Email</span>
              <input :value="user.email" disabled class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-400" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Organization</span>
              <input v-model="profileForm.organization" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Country</span>
              <input v-model="profileForm.country" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
            </label>
          </div>
          <div class="mt-5 flex flex-wrap gap-3">
            <button
              class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
              :disabled="isSavingProfile"
              @click="updateProfile()"
            >
              {{ isSavingProfile ? 'Saving…' : 'Update Profile' }}
            </button>
            <button class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50" @click="showPasswordForm = !showPasswordForm">
              Change Password
            </button>
          </div>
        </div>

        <div v-if="showPasswordForm" class="rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-bold text-slate-900">Change Password</h2>

          <p v-if="passwordSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Password updated.</p>
          <p v-if="passwordError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ passwordError }}</p>

          <div class="mt-5 grid gap-4 md:grid-cols-2">
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">Current Password</span>
              <input v-model="passwordForm.current" type="password" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
            </label>
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-slate-700">New Password</span>
              <input v-model="passwordForm.next" type="password" minlength="8" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
            </label>
          </div>
          <div class="mt-5">
            <button
              class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
              :disabled="isSavingPassword"
              @click="changePassword()"
            >
              {{ isSavingPassword ? 'Updating…' : 'Update Password' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <div v-else-if="loadError" class="rounded-[28px] border border-rose-100 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">{{ loadError }}</div>
    <div v-else class="rounded-[28px] border border-slate-100 bg-white py-16 text-center shadow-sm text-sm text-slate-500">Loading profile…</div>
  </WorkspaceShell>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import api from '@/services/api'

const user = ref(null)
const loadError = ref('')

const profileForm = ref({ full_name: '', organization: '', country: '' })
const isSavingProfile = ref(false)
const profileError = ref('')
const profileSuccess = ref(false)

const showPasswordForm = ref(false)
const passwordForm = ref({ current: '', next: '' })
const isSavingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref(false)

async function fetchProfile() {
  loadError.value = ''
  try {
    const { data } = await api.get('users/me')
    user.value = data
    profileForm.value = { full_name: data.full_name, organization: data.organization || '', country: data.country || '' }
  } catch (error) {
    loadError.value = error.response?.data?.detail || 'Unable to load your profile.'
  }
}

onMounted(fetchProfile)

const initial = computed(() => (user.value?.full_name || '?').charAt(0).toUpperCase())

async function updateProfile() {
  isSavingProfile.value = true
  profileError.value = ''
  profileSuccess.value = false
  try {
    const { data } = await api.put('users/me', profileForm.value)
    user.value = data
    profileSuccess.value = true
  } catch (error) {
    profileError.value = error.response?.data?.detail || 'Unable to update your profile.'
  } finally {
    isSavingProfile.value = false
  }
}

async function changePassword() {
  isSavingPassword.value = true
  passwordError.value = ''
  passwordSuccess.value = false
  try {
    await api.post('users/me/password', {
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.next,
    })
    passwordSuccess.value = true
    passwordForm.value = { current: '', next: '' }
  } catch (error) {
    passwordError.value = error.response?.data?.detail || 'Unable to update your password.'
  } finally {
    isSavingPassword.value = false
  }
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
