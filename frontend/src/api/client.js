import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const detail = error?.response?.data?.detail
    let message = error.message || 'Request failed'
    if (typeof detail === 'string') message = detail
    else if (detail && typeof detail.message === 'string') message = detail.message
    error.userMessage = message
    error.status = error?.response?.status
    return Promise.reject(error)
  }
)

const unwrap = (p) => p.then((r) => r.data)

// ============================================================
// CASES
// ============================================================
export const casesApi = {
  list: (params) => unwrap(api.get('/api/cases/', { params })),
  get: (id) => unwrap(api.get(`/api/cases/${id}`)),
  create: (payload) => unwrap(api.post('/api/cases/', payload)),
  update: (id, payload) => unwrap(api.put(`/api/cases/${id}`, payload)),
  remove: (id) => unwrap(api.delete(`/api/cases/${id}`)),
}

// ============================================================
// CHRONO (Events)
// ============================================================
export const chronoApi = {
  listByCase: (caseId) => unwrap(api.get(`/api/cases/${caseId}/events`)),
  get: (id) => unwrap(api.get(`/api/events/${id}`)),
  create: (caseId, payload) =>
    unwrap(api.post(`/api/cases/${caseId}/events`, payload)),
  update: (id, payload) => unwrap(api.put(`/api/events/${id}`, payload)),
  remove: (id) => unwrap(api.delete(`/api/events/${id}`)),
  overlaps: (caseId) =>
    unwrap(api.get(`/api/cases/${caseId}/events/overlaps`)),
}

// ============================================================
// EVIDENTIA (Evidence)
// ============================================================
export const evidentiaApi = {
  listByCase: (caseId) => unwrap(api.get(`/api/cases/${caseId}/evidence`)),
  get: (id) => unwrap(api.get(`/api/evidence/${id}`)),
  upload: (caseId, formData) =>
    unwrap(
      api.post(`/api/cases/${caseId}/evidence`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    ),
  verify: (id) => unwrap(api.post(`/api/evidence/${id}/verify`)),
  remove: (id) => unwrap(api.delete(`/api/evidence/${id}`)),
}

// ============================================================
// NEXUS (Entities + Relationships + Graph)
// ============================================================
export const nexusApi = {
  listEntities: (caseId) => unwrap(api.get(`/api/cases/${caseId}/entities`)),
  createEntity: (caseId, payload) =>
    unwrap(api.post(`/api/cases/${caseId}/entities`, payload)),
  updateEntity: (id, payload) => unwrap(api.put(`/api/entities/${id}`, payload)),
  removeEntity: (id) => unwrap(api.delete(`/api/entities/${id}`)),

  listRelationships: (caseId) =>
    unwrap(api.get(`/api/cases/${caseId}/relationships`)),
  createRelationship: (caseId, payload) =>
    unwrap(api.post(`/api/cases/${caseId}/relationships`, payload)),
  updateRelationship: (id, payload) =>
    unwrap(api.put(`/api/relationships/${id}`, payload)),
  removeRelationship: (id) => unwrap(api.delete(`/api/relationships/${id}`)),

  graph: (caseId) => unwrap(api.get(`/api/cases/${caseId}/graph`)),
}
