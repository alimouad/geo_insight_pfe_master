import L from 'leaflet'

// leaflet-draw is a legacy UMD-style plugin that attaches itself to a
// global `window.L`. Importing this module (before importing 'leaflet-draw')
// guarantees `window.L` is set first — ES module imports are hoisted, so a
// plain assignment placed between import statements in the same file would
// NOT run in time.
if (typeof window !== 'undefined') {
  window.L = window.L || L
}

export default L
