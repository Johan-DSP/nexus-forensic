import { useEffect, useState } from 'react'
import { Modal, Button, Field, ErrorBanner } from '../ui'
import { chronoApi } from '../../api/client'
import { EVENT_TYPES, CERTAINTY_LEVELS } from '../../lib/format'

const EMPTY = {
  title: '',
  description: '',
  event_type: 'OBSERVATION',
  start_datetime: '',
  end_datetime: '',
  location: '',
  source: '',
  certainty: 'UNKNOWN',
}

function toLocalInput(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function fromLocalInput(v) {
  if (!v) return null
  const d = new Date(v)
  return Number.isNaN(d.getTime()) ? null : d.toISOString()
}

export default function EventFormModal({ open, onClose, caseId, initial, onSaved }) {
  const isEdit = Boolean(initial?.id)
  const [form, setForm] = useState(EMPTY)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) return
    setError(null)
    if (isEdit) {
      setForm({
        title: initial.title || '',
        description: initial.description || '',
        event_type: initial.event_type || 'OBSERVATION',
        start_datetime: toLocalInput(initial.start_datetime),
        end_datetime: toLocalInput(initial.end_datetime),
        location: initial.location || '',
        source: initial.source || '',
        certainty: initial.certainty || 'UNKNOWN',
      })
    } else {
      setForm(EMPTY)
    }
  }, [open, initial, isEdit])

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        title: form.title,
        description: form.description || null,
        event_type: form.event_type,
        start_datetime: fromLocalInput(form.start_datetime),
        end_datetime: fromLocalInput(form.end_datetime),
        location: form.location || null,
        source: form.source || null,
        certainty: form.certainty,
      }
      if (isEdit) {
        await chronoApi.update(initial.id, payload)
      } else {
        await chronoApi.create(caseId, payload)
      }
      onSaved?.()
    } catch (err) {
      setError(err.userMessage || 'No se pudo guardar el evento')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Editar evento' : 'Nuevo evento'}
      size="lg"
    >
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <Field label="Título">
          <input
            className="input"
            value={form.title}
            onChange={(e) => update('title', e.target.value)}
            required
            maxLength={200}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Tipo de evento">
            <select
              className="input"
              value={form.event_type}
              onChange={(e) => update('event_type', e.target.value)}
            >
              {EVENT_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </Field>
          <Field label="Certeza">
            <select
              className="input"
              value={form.certainty}
              onChange={(e) => update('certainty', e.target.value)}
            >
              {CERTAINTY_LEVELS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Inicio">
            <input
              type="datetime-local"
              className="input"
              value={form.start_datetime}
              onChange={(e) => update('start_datetime', e.target.value)}
              required
            />
          </Field>
          <Field label="Fin" hint="Opcional">
            <input
              type="datetime-local"
              className="input"
              value={form.end_datetime}
              onChange={(e) => update('end_datetime', e.target.value)}
            />
          </Field>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Ubicación">
            <input
              className="input"
              value={form.location}
              onChange={(e) => update('location', e.target.value)}
              maxLength={200}
            />
          </Field>
          <Field label="Fuente">
            <input
              className="input"
              value={form.source}
              onChange={(e) => update('source', e.target.value)}
              maxLength={200}
            />
          </Field>
        </div>

        <Field label="Descripción">
          <textarea
            className="input min-h-[80px] resize-y"
            value={form.description}
            onChange={(e) => update('description', e.target.value)}
          />
        </Field>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" type="button" onClick={onClose} disabled={submitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={submitting}>
            {isEdit ? 'Guardar' : 'Crear evento'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
