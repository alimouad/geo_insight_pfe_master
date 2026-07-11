<template>
  <div class="h-full w-full">
    <LMap :zoom="6" :center="[31.5, -6.5]" :useGlobalLeaflet="false" class="h-full w-full" @ready="onMapReady">
      <LTileLayer :url="basemap.url" :attribution="basemap.attribution" />
    </LMap>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'
import L from '@/utils/leaflet-global'
import 'leaflet-draw'
import 'leaflet-draw/dist/leaflet.draw.css'
import { polygonAreaHectares } from '@/utils/geo'
import { usePreferencesStore } from '@/stores/preferences'

const emit = defineEmits(['change'])

const preferences = usePreferencesStore()
onMounted(() => preferences.load())
const basemap = computed(() => preferences.basemap)

function onMapReady(map) {
  // The map can initialize before its container has settled its final size
  // (e.g. inside a flex/tab layout), which leaves Leaflet rendering into a
  // 0x0 box that never repaints. Force a resize check once mounted, and
  // keep watching the container in case the layout shifts afterwards.
  requestAnimationFrame(() => map.invalidateSize())
  setTimeout(() => map.invalidateSize(), 250)

  const resizeObserver = new ResizeObserver(() => map.invalidateSize())
  resizeObserver.observe(map.getContainer())

  const drawnItems = new L.FeatureGroup()
  map.addLayer(drawnItems)

  const drawControl = new L.Control.Draw({
    edit: {
      featureGroup: drawnItems,
    },
    draw: {
      polygon: { allowIntersection: false, showArea: true },
      rectangle: true,
      circle: true,
      circlemarker: false,
      marker: false,
      polyline: false,
    },
  })
  map.addControl(drawControl)

  const circleToPolygon = (layer, sides = 64) => {
    const center = layer.getLatLng()
    const radius = layer.getRadius()
    const earthRadius = 6378137
    const coords = []
    for (let i = 0; i <= sides; i++) {
      const angle = (i / sides) * 2 * Math.PI
      const dx = radius * Math.cos(angle)
      const dy = radius * Math.sin(angle)
      const lat = center.lat + (dy / earthRadius) * (180 / Math.PI)
      const lng = center.lng + ((dx / earthRadius) * (180 / Math.PI)) / Math.cos((center.lat * Math.PI) / 180)
      coords.push([lng, lat])
    }
    return { type: 'Polygon', coordinates: [coords] }
  }

  const emitFromLayers = () => {
    const layer = drawnItems.getLayers()[0]
    if (!layer) {
      emit('change', { geometry: null, areaHa: 0 })
      return
    }
    const geometry = layer instanceof L.Circle ? circleToPolygon(layer) : layer.toGeoJSON().geometry
    emit('change', { geometry, areaHa: polygonAreaHectares(geometry) })
  }

  map.on(L.Draw.Event.CREATED, (e) => {
    drawnItems.clearLayers()
    drawnItems.addLayer(e.layer)
    emitFromLayers()
  })

  map.on(L.Draw.Event.EDITED, emitFromLayers)
  map.on(L.Draw.Event.DELETED, emitFromLayers)
}
</script>
