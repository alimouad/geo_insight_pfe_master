import { defineStore } from 'pinia'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loaded: false,
  }),
  getters: {
    isAdmin: (state) => state.user?.role === 'Admin',
  },
  actions: {
    async load() {
      if (this.loaded) return
      try {
        const { data } = await api.get('users/me')
        this.user = data
        this.loaded = true
      } catch {
        this.user = null
      }
    },
    clear() {
      this.user = null
      this.loaded = false
    },
  },
})
