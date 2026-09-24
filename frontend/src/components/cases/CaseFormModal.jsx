import { useEffect, useState } from 'react'
import { Modal, Button, Field, ErrorBanner } from '../ui'
import { casesApi } from '../../api/client'
import { CASE_STATUS_OPTIONS } from '../../lib/format'

const EMPTY = {
  case_number: '',
  title: '',
  description: '',
  status: 'OPEN',
}

export default function CaseFormModal({ open, onClose, onSaved, initial = null }) {
  const isEdit = Boolean(initial?.id)
  const [form, setForm] = useState(EMPTY)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) return
    setError(null)
    setForm(
      isEdit
        ? {
            case_number: initial.case_number || '',
            title: initial.title || '',
            description: initial.description || '',
            status: initial.status || 'OPEN',
          }
        : EMPTY
    )
  }, [open, initial, isEdit])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function submit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (isEdit) {
        await casesApi.update(initial.id, {
          title: form.title,
          description: form.description || null,
          status: form.status,
        })
      } else {
        await casesApi.create({
          case_number: form.case_number,
          title: form.title,
          description: form.description || null,
          status: form.status,
        })
      }
      onSaved?.()
    } catch (err) {
      setError(err.userMessage || 'No se pudo guardar el caso')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Editar caso' : 'Nuevo caso'}
    >
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <Field label="Número de caso" hint="Identificador único. Ej: CASO-2026-001">
          <input
            className="input font-mono"
            value={form.case_number}
            onChange={(e) => update('case_number', e.target.value)}
            required
            maxLength={50}
            disabled={isEdit}
            placeholder="CASO-2026-001"
          />
        </Field>

        <Field label="Título">
          <input
            className="input"
            value={form.title}
            onChange={(e) => update('title', e.target.value)}
            required
            maxLength={200}
            placeholder="Operación Fénix"
          />
        </Field>

        <Field label="Descripción">
          <textarea
            className="input min-h-[90px] resize-y"
            value={form.description}
            onChange={(e) => update('description', e.target.value)}
            placeholder="Resumen del caso…"
          />
        </Field>

        <Field label="Estado">
          <select
            className="input"
            value={form.status}
            onChange={(e) => update('status', e.target.value)}
          >
            {CASE_STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </Field>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" type="button" onClick={onClose} disabled={submitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={submitting}>
            {isEdit ? 'Guardar cambios' : 'Crear caso'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
