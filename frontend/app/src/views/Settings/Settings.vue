<template>
  <WorkspaceShell
    title="Settings"
    subtitle="Manage your account and application preferences."
  >
    <section>
      <div class="mb-6 flex flex-wrap gap-1 rounded-xl bg-white p-1 shadow-sm border border-slate-100 w-fit">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="rounded-lg px-4 py-1.5 text-sm font-semibold transition"
          :class="activeTab === tab ? 'bg-[#6366f1] text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <!-- Profile -->
      <div v-if="activeTab === 'Profile'" class="max-w-2xl rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">👤 Profile</h2>

        <p v-if="profileSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Profile updated.</p>
        <p v-if="profileError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ profileError }}</p>

        <div v-if="user" class="mt-5 grid gap-4 md:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Full Name</span>
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

        <div class="mt-6 border-t border-slate-100 pt-5">
          <button
            class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
            :disabled="isSavingProfile"
            @click="saveProfile()"
          >
            {{ isSavingProfile ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>
      </div>

      <!-- Security -->
      <div v-if="activeTab === 'Security'" class="max-w-2xl rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">🔒 Security</h2>

        <p v-if="passwordSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Password updated.</p>
        <p v-if="passwordError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ passwordError }}</p>

        <div class="mt-5 space-y-4">
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Current Password</span>
            <input v-model="passwordForm.current" type="password" class="w-full max-w-sm rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">New Password</span>
            <input v-model="passwordForm.next" type="password" minlength="8" class="w-full max-w-sm rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Confirm Password</span>
            <input v-model="passwordForm.confirm" type="password" minlength="8" class="w-full max-w-sm rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]" />
          </label>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-5">
          <button
            class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
            :disabled="isSavingPassword"
            @click="changePassword()"
          >
            {{ isSavingPassword ? 'Updating…' : 'Change Password' }}
          </button>
        </div>
      </div>

      <!-- Preferences -->
      <div v-if="activeTab === 'Preferences'" class="max-w-2xl rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
        <h2 class="text-lg font-bold text-slate-900">⚙ Preferences</h2>

        <p v-if="preferencesSuccess" class="mt-4 rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-xs font-semibold text-emerald-600">Preferences saved.</p>
        <p v-if="preferencesError" class="mt-4 rounded-2xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs font-semibold text-rose-600">{{ preferencesError }}</p>

        <div v-if="preferences" class="mt-5 space-y-5">
          <div>
            <p class="mb-2 text-xs font-semibold text-slate-700">Theme</p>
            <div class="flex gap-1 rounded-xl bg-slate-50 p-1 sm:w-64">
              <button
                v-for="opt in ['light', 'dark']"
                :key="opt"
                class="flex-1 rounded-lg px-3 py-1.5 text-xs font-semibold capitalize transition"
                :class="preferences.theme === opt ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                @click="preferences.theme = opt"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <div>
            <p class="mb-2 text-xs font-semibold text-slate-700">Default Map</p>
            <div class="flex flex-wrap gap-1 rounded-xl bg-slate-50 p-1 sm:w-96">
              <button
                v-for="opt in ['OpenStreetMap', 'Satellite', 'Terrain']"
                :key="opt"
                class="flex-1 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold transition"
                :class="preferences.default_basemap === opt ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                @click="preferences.default_basemap = opt"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <label class="block sm:w-64">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Default Language</span>
            <select v-model="preferences.language" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option value="en">English</option>
              <option value="fr">French</option>
              <option value="ar">Arabic</option>
            </select>
          </label>

          <label class="block sm:w-64">
            <span class="mb-1.5 block text-xs font-semibold text-slate-700">Default Coordinate System</span>
            <select v-model="preferences.default_projection" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700 outline-none focus:border-[#6366f1]">
              <option value="EPSG:4326">EPSG:4326</option>
              <option value="EPSG:3857">EPSG:3857</option>
              <option value="EPSG:26191">EPSG:26191</option>
            </select>
          </label>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-5">
          <button
            class="rounded-xl bg-[#6366f1] px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-[#5558e6] disabled:opacity-60"
            :disabled="isSavingPreferences"
            @click="savePreferences()"
          >
            {{ isSavingPreferences ? 'Saving…' : 'Save Preferences' }}
          </button>
        </div>
      </div>

      <!-- About -->
      <div v-if="activeTab === 'About'" class="max-w-2xl rounded-[28px] border border-slate-100 bg-white p-6 shadow-sm">
        <div class="text-center">
          <p class="text-2xl font-black text-slate-900">🌍 GeoInsight</p>
          <p class="mt-1 text-sm text-slate-500">Version 1.0.0</p>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-6">
          <p class="text-sm leading-relaxed text-slate-600">
            GeoInsight is a Web GIS platform designed for geospatial analysis and environmental monitoring using Google Earth Engine.
          </p>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-6">
          <p class="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Developed By</p>
          <div class="mt-2 space-y-0.5 text-sm text-slate-700">
            <p class="font-semibold">Mouad Ali</p>
            <p>Master GAGE</p>
            <p>Faculty of Sciences Ben M'Sik</p>
            <p>Hassan II University of Casablanca</p>
          </div>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-6">
          <p class="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Technologies</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <span v-for="tech in technologies" :key="tech" class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">{{ tech }}</span>
          </div>
        </div>

        <div class="mt-6 border-t border-slate-100 pt-6 text-center text-xs text-slate-400">
          © 2026 GeoInsight
        </div>
      </div>
    </section>
  </WorkspaceShell>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import WorkspaceShell from '@/components/Layout/WorkspaceShell.vue'
import api from '@/services/api'
import { usePreferencesStore } from '@/stores/preferences'

const preferencesStore = usePreferencesStore()

const tabs = ['Profile', 'Security', 'Preferences', 'About']
const technologies = ['Vue.js', 'FastAPI', 'PostgreSQL/PostGIS', 'Google Earth Engine', 'Leaflet', 'Docker']
const activeTab = ref('Profile')

const user = ref(null)
const profileForm = ref({ full_name: '', organization: '', country: '' })
const isSavingProfile = ref(false)
const profileError = ref('')
const profileSuccess = ref(false)

const passwordForm = ref({ current: '', next: '', confirm: '' })
const isSavingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref(false)

const preferences = ref(null)
const isSavingPreferences = ref(false)
const preferencesError = ref('')
const preferencesSuccess = ref(false)

async function fetchProfile() {
  try {
    const { data } = await api.get('users/me')
    user.value = data
    profileForm.value = { full_name: data.full_name, organization: data.organization || '', country: data.country || '' }
  } catch (error) {
    profileError.value = error.response?.data?.detail || 'Unable to load your profile.'
  }
}

async function fetchPreferences() {
  try {
    const { data } = await api.get('users/preferences')
    preferences.value = data
    preferencesStore.setFromResponse(data)
  } catch (error) {
    preferencesError.value = error.response?.data?.detail || 'Unable to load your preferences.'
  }
}

onMounted(() => {
  fetchProfile()
  fetchPreferences()
})

async function saveProfile() {
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
  passwordError.value = ''
  passwordSuccess.value = false
  if (passwordForm.value.next !== passwordForm.value.confirm) {
    passwordError.value = 'New password and confirmation do not match.'
    return
  }
  isSavingPassword.value = true
  try {
    await api.post('users/me/password', {
      current_password: passwordForm.value.current,
      new_password: passwordForm.value.next,
    })
    passwordSuccess.value = true
    passwordForm.value = { current: '', next: '', confirm: '' }
  } catch (error) {
    passwordError.value = error.response?.data?.detail || 'Unable to update your password.'
  } finally {
    isSavingPassword.value = false
  }
}

async function savePreferences() {
  isSavingPreferences.value = true
  preferencesError.value = ''
  preferencesSuccess.value = false
  try {
    const { data } = await api.put('users/preferences', preferences.value)
    preferences.value = data
    preferencesStore.setFromResponse(data)
    preferencesSuccess.value = true
  } catch (error) {
    preferencesError.value = error.response?.data?.detail || 'Unable to save your preferences.'
  } finally {
    isSavingPreferences.value = false
  }
}
</script>
