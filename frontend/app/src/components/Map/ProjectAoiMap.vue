<template>
  <div class="relative h-full w-full">
    <LMap ref="mapRef" :zoom="zoom" :center="center" :useGlobalLeaflet="false" class="h-full w-full" @ready="fitToPolygon">
      <LTileLayer
        :url="basemap.url"
        :attribution="basemap.attribution"
      />
      <LTileLayer v-if="overlayUrl" :url="overlayUrl" :opacity="0.75" />
      <LPolygon
        v-if="polygon && polygon.length"
        :lat-lngs="polygon"
        color="#6366f1"
        :fill-color="'#6366f1'"
        :fill-opacity="overlayUrl ? 0 : 0.15"
        :weight="2"
      />
    </LMap>
    <div v-if="!polygon || !polygon.length" class="pointer-events-none absolute inset-0 flex items-center justify-center bg-white/60 text-sm font-semibold text-slate-500">
      No AOI defined for this project yet.
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { LMap, LTileLayer, LPolygon } from '@vue-leaflet/vue-leaflet'
import { usePreferencesStore } from '@/stores/preferences'

const props = defineProps({
  center: { type: Array, required: true },
  polygon: { type: Array, default: () => [] },
  zoom: { type: Number, default: 11 },
  overlayUrl: { type: String, default: null },
})

const preferences = usePreferencesStore()
onMounted(() => preferences.load())
const basemap = computed(() => preferences.basemap)

const mapRef = ref(null)

function fitToPolygon() {
  const map = mapRef.value?.leafletObject
  if (!map || !props.polygon || !props.polygon.length) return
  const lats = props.polygon.map((c) => c[0])
  const lngs = props.polygon.map((c) => c[1])
  const sw = [Math.min(...lats), Math.min(...lngs)]
  const ne = [Math.max(...lats), Math.max(...lngs)]
  map.fitBounds([sw, ne], { padding: [24, 24], maxZoom: 15 })
}

watch(
  () => props.polygon,
  () => nextTick(fitToPolygon),
  { deep: true, immediate: true },
)
</script>
