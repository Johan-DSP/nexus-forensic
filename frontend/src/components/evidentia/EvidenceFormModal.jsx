import { useEffect, useRef, useState } from 'react'
import { Modal, Button, Field, ErrorBanner } from '../ui'
import { evidentiaApi } from '../../api/client'
import { formatFileSize } from '../../lib/format'

const EMPTY = {
  description: '',
  source: '',
  acquired_at: '',
}

export default function EvidenceFormModal({ open, onClose, caseId, onSaved }) {
  const [form, setForm] = useState(EMPTY)
  const [file, setFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!open) return
    setForm(EMPTY)
    setFile(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ''
  }, [open])

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    if (!file) {
      setError('Selecciona un archivo para subir')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      if (form.description) fd.append('description', form.description)
      if (form.source) fd.append('source', form.source)
      if (form.acquired_at) {
        fd.append('acquired_at', new Date(form.acquired_at).toISOString())
      }
      await evidentiaApi.upload(caseId, fd)
      onSaved?.()
    } catch (err) {
      setError(err.userMessage || 'No se pudo subir la evidencia')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Subir evidencia">
      <form onSubmit={submit} className="space-y-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

        <Field label="Archivo">
          <input
            ref={inputRef}
            type="file"
            className="input file:mr-3 file:rounded file:border-0 file:bg-slate-800 file:px-3 file:py-1.5 file:text-xs file:text-slate-200"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          {file && (
            <p className="mt-1.5 text-[11px] text-slate-500">
              {file.name} · {formatFileSize(file.size)}
            </p>
          )}
        </Field>

        <Field label="Descripción">
          <textarea
            className="input min-h-[80px] resize-y"
            value={form.description}
            onChange={(e) => update('description', e.target.value)}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Fuente">
            <input
              className="input"
              value={form.source}
              onChange={(e) => update('source', e.target.value)}
              maxLength={200}
            />
          </Field>
          <Field label="Fecha de adquisición">
            <input
              type="datetime-local"
              className="input"
              value={form.acquired_at}
              onChange={(e) => update('acquired_at', e.target.value)}
            />
          </Field>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="ghost" type="button" onClick={onClose} disabled={submitting}>
            Cancelar
          </Button>
          <Button type="submit" loading={submitting}>
            Subir
          </Button>
        </div>
      </form>
    </Modal>
  )
}
