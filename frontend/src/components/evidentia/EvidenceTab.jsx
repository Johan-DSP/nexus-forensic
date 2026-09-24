import { useEffect, useState } from 'react'
import {
  Upload, FileText, Trash2, ShieldCheck, ShieldAlert, ExternalLink, Paperclip,
} from 'lucide-react'
import { evidentiaApi } from '../../api/client'
import {
  Button, Card, Spinner, ErrorBanner, EmptyState, Badge, ConfirmDialog,
} from '../ui'
import { formatDateTime, formatFileSize, truncateHash } from '../../lib/format'
import EvidenceFormModal from './EvidenceFormModal'

export default function EvidenceTab({ caseId }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleting, setDeleting] = useState(null)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [verifying, setVerifying] = useState(null)
  const [verifyResult, setVerifyResult] = useState({})

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setItems(await evidentiaApi.listByCase(caseId))
    } catch (err) {
      setError(err.userMessage || 'Error al cargar evidencias')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() /* eslint-disable-next-line */ }, [caseId])

  async function handleVerify(id) {
    setVerifying(id)
    try {
      const res = await evidentiaApi.verify(id)
      setVerifyResult((s) => ({ ...s, [id]: res }))
    } catch (err) {
      setVerifyResult((s) => ({
        ...s,
        [id]: { match: false, message: err.userMessage || 'Error de verificación' },
      }))
    } finally {
      setVerifying(null)
    }
  }

  async function handleDelete() {
    if (!deleting) return
    setDeleteLoading(true)
    try {
      await evidentiaApi.remove(deleting.id)
      setDeleting(null)
      await load()
    } catch (err) {
      setError(err.userMessage || 'No se pudo eliminar la evidencia')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Evidencias</h2>
          <p className="text-xs text-slate-500">
            {items.length} archivo{items.length !== 1 ? 's' : ''} · integridad SHA-256
          </p>
        </div>
        <Button onClick={() => setUploadOpen(true)}>
          <Upload className="h-4 w-4" /> Subir evidencia
        </Button>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <Spinner label="Cargando evidencias…" />
      ) : items.length === 0 ? (
        <Card>
          <EmptyState
            icon={Paperclip}
            title="Sin evidencias"
            description="Sube el primer archivo para comenzar la cadena de custodia."
            action={
              <Button onClick={() => setUploadOpen(true)}>
                <Upload className="h-4 w-4" /> Subir evidencia
              </Button>
            }
          />
        </Card>
      ) : (
        <ul className="space-y-3">
          {items.map((ev) => {
            const result = verifyResult[ev.id]
            return (
              <li key={ev.id}>
                <Card className="p-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 flex-shrink-0 text-slate-500" />
                        <span className="truncate text-sm font-medium text-slate-100">
                          {ev.original_filename}
                        </span>
                      </div>

                      <div className="mt-2 flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
                        <span className="font-mono">
                          {truncateHash(ev.sha256)}
                        </span>
                        <span>{formatFileSize(ev.file_size)}</span>
                        <span>{ev.mime_type}</span>
                        {ev.acquired_at && (
                          <span>Adquirida: {formatDateTime(ev.acquired_at)}</span>
                        )}
                      </div>

                      {ev.description && (
                        <p className="mt-2 text-xs text-slate-400">
                          {ev.description}
                        </p>
                      )}

                      {result && (
                        <div
                          className={`mt-3 flex items-center gap-2 rounded-md px-3 py-2 text-xs ${
                            result.match
                              ? 'bg-emerald-950/40 text-emerald-300'
                              : 'bg-red-950/40 text-red-300'
                          }`}
                        >
                          {result.match ? (
                            <ShieldCheck className="h-4 w-4" />
                          ) : (
                            <ShieldAlert className="h-4 w-4" />
                          )}
                          <span>{result.message}</span>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        loading={verifying === ev.id}
                        onClick={() => handleVerify(ev.id)}
                        title="Verificar integridad"
                      >
                        <ShieldCheck className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDeleting(ev)}
                        title="Eliminar"
                      >
                        <Trash2 className="h-3.5 w-3.5 text-red-400" />
                      </Button>
                    </div>
                  </div>
                </Card>
              </li>
            )
          })}
        </ul>
      )}

      <EvidenceFormModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        caseId={caseId}
        onSaved={async () => { setUploadOpen(false); await load() }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={handleDelete}
        loading={deleteLoading}
        title="Eliminar evidencia"
        message={`¿Eliminar "${deleting?.original_filename}"? Esta acción es irreversible.`}
      />
    </div>
  )
}
