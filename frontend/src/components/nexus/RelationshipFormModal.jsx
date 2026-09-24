import { useEffect, useState } from 'react'
import { Modal, Button, Field, ErrorBanner } from '../ui'
import { nexusApi } from '../../api/client'
import { RELATIONSHIP_TYPES } from '../../lib/format'

const EMPTY = {
  source_entity_id: '',
  target_entity_id: '',
  relationship_type: 'ASSOCIATED_WITH',
  description: '',
  confidence: '',
}

export default function RelationshipFormModal({
  open, onClose, caseId, entities, initial, onSaved,
}) {
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
            source_entity_id: initial.source_entity_id,
            target_entity_id: initial.target_entity_id,
            relationship_type: initial.relationship_type || 'ASSOCIATED_WITH',
            description: initial.description || '',
            confidence: initial.confidence ?? '',
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
      const confidence =
        form.confidence === '' ? null : Number(form.confidence)

      if (isEdit) {
        await nexusApi.updateRelationship(initial.id, {
          relationship_type: form.relationship_type,
          description: form.description || null,
          confidence,
        })
      } else {
        await nexusApi.createRelationship(caseId, {
          source_entity_id: Number(form.source_entity_id),
          target_entity_id: Number(form.target_entity_id),
          relationship_type: form.relationship_type,
          description: form.description || null,
          confidence,
        })
      }
      onSaved?.()
    } catch (err) {
      setError(err.userMessage || 'No se pudo guardar la relación')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? 'Editar relación' : 'Nueva relación'}
    >
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Origen">
            <select
              className="input"
              value={form.source_entity_id}
              onChange={(e) => update('source_entity_id', e.target.value)}
              disabled={isEdit}
              required
            >
              <option value="">Selecciona…</option>
              {entities.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.type})
                </option>
              ))}
            </select>
          </Field>
          <Field label="Destino">
            <select
              className="input"
              value={form.target_entity_id}
              onChange={(e) => update('target_entity_id', e.target.value)}
              disabled={isEdit}
              required
            >
              <option value="">Selecciona…</option>
              {entities.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name} ({e.type})
                </option>
              ))}
            </select>
          </Field>
        </div>

        <Field label="Tipo de relación">
          <select
            className="input"
            value={form.relationship_type}
            onChange={(e) => update('relationship_type', e.target.value)}
          >
            {RELATIONSHIP_TYPES.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </Field>

        <Field label="Confianza" hint="0 a 1 (opcional)">
          <input
            type="number"
            className="input"
            min="0" max="1" step="0.05"
            value={form.confidence}
            onChange={(e) => update('confidence', e.target.value)}
          />
        </Field>

        <Field label="Descripción">
          <textarea
            className="input min-h-[70px] resize-y"
            value={form.description}
            onChange={(e) => update('description', e.target.value)}
          />
        </Field>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" type="button" onClick={onClose} disabled={submitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={submitting}>
            {isEdit ? 'Guardar' : 'Crear relación'}
          </Button>
        </div>
      </form>
    </Modal>
  )
}
