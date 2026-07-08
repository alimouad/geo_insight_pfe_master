const EARTH_RADIUS_M = 6378137

function toRad(deg) {
  return (deg * Math.PI) / 180
}

// Approximate planar area (equirectangular projection centered on the ring's
// mean latitude) — good enough for typical AOI sizes (a few km to a few
// hundred km across), avoids pulling in a full geodesy library for this.
function ringAreaSquareMeters(ring) {
  if (ring.length < 3) return 0

  const meanLat = ring.reduce((sum, [, lat]) => sum + lat, 0) / ring.length
  const cosLat = Math.cos(toRad(meanLat))

  const points = ring.map(([lng, lat]) => [
    toRad(lng) * EARTH_RADIUS_M * cosLat,
    toRad(lat) * EARTH_RADIUS_M,
  ])

  let sum = 0
  for (let i = 0; i < points.length; i++) {
    const [x1, y1] = points[i]
    const [x2, y2] = points[(i + 1) % points.length]
    sum += x1 * y2 - x2 * y1
  }

  return Math.abs(sum / 2)
}

export function polygonAreaHectares(geometry) {
  if (!geometry) return 0

  const rings = geometry.type === 'Polygon' ? [geometry.coordinates[0]] : geometry.coordinates.map((poly) => poly[0])

  const totalSquareMeters = rings.reduce((sum, ring) => sum + ringAreaSquareMeters(ring), 0)
  return totalSquareMeters / 10_000
}
