import { useEffect, useMemo, useState } from 'react'
import {
  Plus, Clock, MapPin, AlertTriangle, Trash2, Pencil, Calendar,
} from 'lucide-react'
import { chronoApi } from '../../api/client'
import {
  Button, Card, Spinner, ErrorBanner, EmptyState, Badge,
  ConfirmDialog, CardHeader,
} from '../ui'
import { formatDateTime, CERTAINTY_COLORS } from '../../lib/format'
import EventFormModal from './EventFormModal'

export default function EventsTab({ caseId }) {
  const [events, setEvents] = useState([])
  const [overlaps, setOverlaps] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [evts, ovls] = await Promise.all([
        chronoApi.listByCase(caseId),
        chronoApi.overlaps(caseId).catch(() => []),
      ])
      setEvents(evts)
      setOverlaps(ovls)
    } catch (err) {
      setError(err.userMessage || 'Error al cargar los eventos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() /* eslint-disable-next-line */ }, [caseId])

  const overlapEventIds = useMemo(() => {
    const s = new Set()
    overlaps.forEach((o) => {
      s.add(o.event_1_id); s.add(o.event_2_id)
    })
    return s
  }, [overlaps])

  async function handleDelete() {
    if (!deleting) return
    setDeleteLoading(true)
    try {
      await chronoApi.remove(deleting.id)
      setDeleting(null)
      await load()
    } catch (err) {
      setError(err.userMessage || 'No se pudo eliminar el evento')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">
            Cronología de eventos
          </h2>
          <p className="text-xs text-slate-500">
            {events.length} evento{events.length !== 1 ? 's' : ''}
            {overlaps.length > 0 && (
              <span className="ml-2 text-amber-400">
                · {overlaps.length} solapamiento{overlaps.length !== 1 ? 's' : ''}
              </span>
            )}
          </p>
        </div>
        <Button onClick={() => { setEditing(null); setFormOpen(true) }}>
          <Plus className="h-4 w-4" /> Nuevo evento
        </Button>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {overlaps.length > 0 && (
        <Card className="border-amber-900/50 bg-amber-950/20 p-4">
          <div className="flex gap-3">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-400" />
            <div className="text-xs text-amber-200">
              <p className="font-medium">
                Se detectaron {overlaps.length} solapamiento
                {overlaps.length !== 1 ? 's' : ''} temporal
                {overlaps.length !== 1 ? 'es' : ''}
              </p>
              <p className="mt-1 text-amber-300/70">
                Los eventos marcados en amarillo se superponen en el tiempo.
              </p>
            </div>
          </div>
        </Card>
      )}

      {loading ? (
        <Spinner label="Cargando eventos…" />
      ) : events.length === 0 ? (
        <Card>
          <EmptyState
            icon={Clock}
            title="Sin eventos registrados"
            description="Añade el primer evento para construir la cronología."
            action={
              <Button onClick={() => { setEditing(null); setFormOpen(true) }}>
                <Plus className="h-4 w-4" /> Añadir evento
              </Button>
            }
          />
        </Card>
      ) : (
        <ol className="space-y-3">
          {events.map((ev) => (
            <EventItem
              key={ev.id}
              event={ev}
              hasOverlap={overlapEventIds.has(ev.id)}
              onEdit={() => { setEditing(ev); setFormOpen(true) }}
              onDelete={() => setDeleting(ev)}
            />
          ))}
        </ol>
      )}

      <EventFormModal
        open={formOpen}
        onClose={() => setFormOpen(false)}
        caseId={caseId}
        initial={editing}
        onSaved={async () => { setFormOpen(false); await load() }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={handleDelete}
        loading={deleteLoading}
        title="Eliminar evento"
        message={`¿Eliminar el evento "${deleting?.title}"?`}
      />
    </div>
  )
}

function EventItem({ event, hasOverlap, onEdit, onDelete }) {
  const cert = CERTAINTY_COLORS[event.certainty] || CERTAINTY_COLORS.UNKNOWN
  return (
    <li>
      <Card
        className={`p-4 transition-colors ${
          hasOverlap ? 'border-amber-900/60 bg-amber-950/10' : ''
        }`}
      >
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-slate-400">
                {event.event_type}
              </span>
              <Badge className={cert}>{event.certainty}</Badge>
              {hasOverlap && (
                <Badge className="bg-amber-500/15 text-amber-300">
                  <AlertTriangle className="h-3 w-3" /> Solapamiento
                </Badge>
              )}
            </div>
            <h3 className="mt-2 text-sm font-semibold text-slate-100">
              {event.title}
            </h3>
            {event.description && (
              <p className="mt-1 text-xs text-slate-400">{event.description}</p>
            )}
            <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formatDateTime(event.start_datetime)}
                {event.end_datetime && ` → ${formatDateTime(event.end_datetime)}`}
              </span>
              {event.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  {event.location}
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={onEdit} aria-label="Editar">
              <Pencil className="h-3.5 w-3.5" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete} aria-label="Eliminar">
              <Trash2 className="h-3.5 w-3.5 text-red-400" />
            </Button>
          </div>
        </div>
      </Card>
    </li>
  )
}
