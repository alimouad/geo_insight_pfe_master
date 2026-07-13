<template>
  <header class="flex items-center justify-between gap-6 shrink-0">
    <div class="min-w-0">
      <p class="text-xs font-semibold uppercase tracking-[0.3em] text-[#0ea5ff]">GeoInsight</p>
      <h1 class="mt-1 text-2xl font-black text-slate-900 tracking-tight">{{ title }}</h1>
      <p class="text-xs text-slate-400 mt-0.5 max-w-3xl">{{ subtitle }}</p>
    </div>

    <div class="flex items-center gap-3">
      <slot name="actions" />

      <div class="relative" ref="menuRef">
        <button
          type="button"
          class="flex items-center gap-2.5 rounded-xl border border-slate-100 bg-white py-1.5 pl-1.5 pr-3 shadow-sm transition hover:border-slate-200 hover:bg-slate-50"
          @click="menuOpen = !menuOpen"
        >
          <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#6366f1] text-xs font-bold text-white">
            {{ initials }}
          </span>
          <span class="hidden text-left sm:block">
            <span class="block text-sm font-semibold leading-tight text-slate-800">{{ auth.user?.full_name || 'Account' }}</span>
            <span class="block text-[11px] leading-tight text-slate-400">{{ auth.user?.role || '—' }}</span>
          </span>
          <svg class="h-4 w-4 text-slate-400 transition" :class="menuOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 9l6 6 6-6" />
          </svg>
        </button>

        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="opacity-0 -translate-y-1"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-1"
        >
          <div v-if="menuOpen" class="absolute right-0 z-20 mt-2 w-56 overflow-hidden rounded-2xl border border-slate-100 bg-white p-1.5 shadow-lg">
            <div class="border-b border-slate-100 px-3 py-2.5 sm:hidden">
              <p class="text-sm font-semibold text-slate-800">{{ auth.user?.full_name || 'Account' }}</p>
              <p class="text-xs text-slate-400">{{ auth.user?.email }}</p>
            </div>
            <p class="hidden truncate px-3 py-1.5 text-xs text-slate-400 sm:block">{{ auth.user?.email }}</p>

            <button type="button" class="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50" @click="goTo('/profile')">
              <svg class="h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              Profile
            </button>
            <button type="button" class="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50" @click="goTo('/settings')">
              <svg class="h-4 w-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              Settings
            </button>

            <div class="my-1 border-t border-slate-100"></div>

            <button type="button" class="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-sm font-medium text-rose-500 transition hover:bg-rose-50" @click="goTo('/logout')">
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Log out
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const { title, subtitle } = defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, required: true },
})

const router = useRouter()
const auth = useAuthStore()
onMounted(() => auth.load())

const menuOpen = ref(false)
const menuRef = ref(null)

function goTo(path) {
  menuOpen.value = false
  router.push(path)
}

function handleClickOutside(event) {
  if (menuOpen.value && menuRef.value && !menuRef.value.contains(event.target)) {
    menuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))

const initials = computed(() => {
  const name = auth.user?.full_name
  if (!name) return '?'
  return name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase()
})
</script>
