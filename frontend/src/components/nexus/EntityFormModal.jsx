import { useEffect, useState } from 'react'
import { Modal, Button, Field, ErrorBanner } from '../ui'
import { nexusApi } from '../../api/client'
import { ENTITY_TYPES } from '../../lib/format'

const EMPTY = {
  type: 'PERSON',
  name: '',
  identifier: '',
  description: '',
}

export default function EntityFormModal({ open, onClose, caseId, initial, onSaved }) {
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
            type: initial.type || 'PERSON',
            name: initial.name || '',
            identifier: initial.identifier || '',
            description: initial.description || '',
          }
        : EMPTY
    )
  }, [open, initial, isEdit])

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        type: form.type,
        name: form.name,
        identifier: form.identifier || null,
        description: form.description || null,
      }
      if (isEdit) {
        await nexusApi.updateEntity(initial.id, payload)
      } else {
        await nexusApi.createEntity(caseId, payload)
      }
      onSaved?.()
    } catch (err) {
      setError(err.userMessage || 'No se pudo guardar la entidad')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? 'Editar entidad' : 'Nueva entidad'}>
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <Field label="Tipo">
          <select
            className="input"
            value={form.type}
            onChange={(e) => update('type', e.target.value)}
          >
            {ENTITY_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </Field>

        <Field label="Nombre">
          <input
            className="input"
            value={form.name}
            onChange={(e) => update('name', e.target.value)}
            required
            maxLength={200}
            placeholder="Ej: Alejandro Vargas"
          />
        </Field>

        <Field label="Identificador" hint="Matrícula, teléfono, DNI, alias…">
          <input
            className="input font-mono"
            value={form.identifier}
            onChange={(e) => update('identifier', e.target.value)}
            maxLength={100}
            placeholder="ABC-123"
          />
        </Field>

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
            {isEdit ? 'Guardar' : 'Crear entidad'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
