<template>
  <div class="relative">
    <LMap :zoom="zoom" :center="center" :useGlobalLeaflet="false" class="h-full w-full">
      <LTileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
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
import { LMap, LTileLayer, LPolygon } from '@vue-leaflet/vue-leaflet'

defineProps({
  center: { type: Array, required: true },
  polygon: { type: Array, default: () => [] },
  zoom: { type: Number, default: 11 },
  overlayUrl: { type: String, default: null },
})
</script>
