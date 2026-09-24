export const CASE_STATUS = {
  OPEN: { label: 'Abierto', className: 'bg-cyan-500/15 text-cyan-300' },
  IN_PROGRESS: { label: 'En progreso', className: 'bg-amber-500/15 text-amber-300' },
  CLOSED: { label: 'Cerrado', className: 'bg-emerald-500/15 text-emerald-300' },
  ARCHIVED: { label: 'Archivado', className: 'bg-slate-500/15 text-slate-400' },
}

export const CASE_STATUS_OPTIONS = Object.entries(CASE_STATUS).map(
  ([value, { label }]) => ({ value, label })
)

export const EVENT_TYPES = [
  'CALL', 'MESSAGE', 'MEETING', 'MOVEMENT', 'OBSERVATION',
  'TRANSACTION', 'INCIDENT', 'DOCUMENT', 'OTHER',
]

export const CERTAINTY_LEVELS = [
  'CONFIRMED', 'REPORTED', 'ESTIMATED', 'UNKNOWN',
]

export const ENTITY_TYPES = [
  'PERSON', 'PHONE', 'EMAIL', 'VEHICLE', 'ADDRESS',
  'ORGANIZATION', 'ACCOUNT', 'LOCATION', 'DOCUMENT', 'DEVICE', 'OTHER',
]

export const RELATIONSHIP_TYPES = [
  'ASSOCIATED_WITH', 'OWNS', 'USES', 'CONTACTED', 'LOCATED_AT',
  'EMPLOYED_BY', 'REGISTERED_TO', 'CONNECTED_TO', 'RELATED_TO', 'OTHER',
]

export const CERTAINTY_COLORS = {
  CONFIRMED: 'bg-emerald-500/15 text-emerald-300',
  REPORTED: 'bg-cyan-500/15 text-cyan-300',
  ESTIMATED: 'bg-amber-500/15 text-amber-300',
  UNKNOWN: 'bg-slate-500/15 text-slate-400',
}

export function formatDateTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleString('es-ES', {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

export function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleDateString('es-ES', {
    year: 'numeric', month: 'short', day: '2-digit',
  })
}

export function formatFileSize(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 ** 3) return `${(bytes / 1024 / 1024).toFixed(2)} MB`
  return `${(bytes / 1024 ** 3).toFixed(2)} GB`
}

export function truncateHash(hash, head = 10, tail = 6) {
  if (!hash || hash.length <= head + tail + 1) return hash || '—'
  return `${hash.slice(0, head)}…${hash.slice(-tail)}`
}

export function relativeTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  const diff = (Date.now() - d.getTime()) / 1000
  const abs = Math.abs(diff)
  if (abs < 60) return 'hace unos segundos'
  if (abs < 3600) return `hace ${Math.round(abs / 60)} min`
  if (abs < 86400) return `hace ${Math.round(abs / 3600)} h`
  if (abs < 604800) return `hace ${Math.round(abs / 86400)} d`
  return formatDate(value)
}
