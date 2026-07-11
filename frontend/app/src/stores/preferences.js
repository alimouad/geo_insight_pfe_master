import { defineStore } from 'pinia'
import api from '@/services/api'

export const BASEMAPS = {
  OpenStreetMap: {
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors',
  },
  Satellite: {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
  },
  Terrain: {
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenTopoMap contributors',
  },
}

export const usePreferencesStore = defineStore('preferences', {
  state: () => ({
    theme: 'light',
    language: 'en',
    defaultBasemap: 'OpenStreetMap',
    defaultProjection: 'EPSG:4326',
    loaded: false,
  }),
  getters: {
    basemap: (state) => BASEMAPS[state.defaultBasemap] || BASEMAPS.OpenStreetMap,
  },
  actions: {
    async load() {
      if (this.loaded) return
      try {
        const { data } = await api.get('users/preferences')
        this.theme = data.theme
        this.language = data.language
        this.defaultBasemap = data.default_basemap
        this.defaultProjection = data.default_projection
        this.loaded = true
      } catch {
        // stay on defaults if not logged in yet or request fails
      }
    },
    setFromResponse(data) {
      this.theme = data.theme
      this.language = data.language
      this.defaultBasemap = data.default_basemap
      this.defaultProjection = data.default_projection
      this.loaded = true
    },
  },
})
