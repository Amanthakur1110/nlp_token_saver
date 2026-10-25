/**
 * api.js – all fetch calls in one place.
 * Components import functions from here; no raw fetch() elsewhere.
 */

const BASE = '/api'

/** Check backend is alive */
export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`)
  return res.json()
}

/** Get list of all techniques with their schemas */
export async function fetchTechniques() {
  const res = await fetch(`${BASE}/techniques`)
  if (!res.ok) throw new Error('Failed to load techniques')
  return res.json()
}

/**
 * Upload a file and get back doc metadata.
 * @param {File} file
 */
export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Upload failed')
  return data
}

/**
 * Run compression on an uploaded document.
 * @param {string} docId
 * @param {Array}  techniques  [{id, params}]
 * @param {string} mode        'individual' | 'chain' | 'both'
 */
export async function runCompress(docId, techniques, mode = 'both') {
  const res = await fetch(`${BASE}/compress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId, techniques, mode }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Compression failed')
  return data
}

/**
 * Apply a named preset.
 * @param {string} docId
 * @param {string} preset  'safe' | 'balanced' | 'max_saver'
 */
export async function runPreset(docId, preset) {
  const res = await fetch(`${BASE}/compress`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doc_id: docId, preset, mode: 'both' }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.error || 'Preset failed')
  return data
}

