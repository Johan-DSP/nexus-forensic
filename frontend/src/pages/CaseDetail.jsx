import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft, Pencil, Trash2, FileText, Clock, Paperclip, Network, Share2,
  Calendar, Hash, Activity,
} from 'lucide-react'
import { casesApi } from '../api/client'
import {
  Button, Card, CardHeader, Spinner, ErrorBanner, Badge, Tabs,
  ConfirmDialog, EmptyState, Field,
} from '../components/ui'
import { CASE_STATUS, formatDateTime } from '../lib/format'
import CaseFormModal from '../components/cases/CaseFormModal'
import EventsTab from '../components/chrono/EventsTab'
import EvidenceTab from '../components/evidentia/EvidenceTab'
import EntitiesTab from '../components/nexus/EntitiesTab'
import NexusGraphTab from '../components/nexus/NexusGraphTab'

export default function CaseDetail() {
  const { id } = useParams()
  const [caseItem, setCaseItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tab, setTab] = useState('overview')
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleting, setDeleting] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const data = await casesApi.get(id)
      setCaseItem(data)
    } catch (err) {
      setError(err.userMessage || 'No se pudo cargar el caso')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    setTab('overview')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  if (loading) return <Spinner label="Cargando caso…" />
  if (error)
    return (
      <div className="space-y-4">
        <ErrorBanner message={error} />
        <Link to="/cases" className="btn btn-secondary">
          <ArrowLeft className="h-4 w-4" /> Volver
        </Link>
      </div>
    )
  if (!caseItem) return null

  const status = CASE_STATUS[caseItem.status] || CASE_STATUS.OPEN

  const tabs = [
    { id: 'overview', label: 'Resumen', icon: FileText },
    { id: 'chrono', label: 'Cronología', icon: Clock },
    { id: 'evidence', label: 'Evidencias', icon: Paperclip },
    { id: 'entities', label: 'Entidades', icon: Network },
    { id: 'graph', label: 'Grafo NEXUS', icon: Share2 },
  ]

  async function handleDelete() {
    setDeleting(true)
    try {
      await casesApi.remove(caseItem.id)
      window.location.href = '/cases'
    } catch (err) {
      setError(err.userMessage || 'No se pudo eliminar el caso')
      setDeleting(false)
      setDeleteOpen(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb + actions */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <Link
            to="/cases"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Casos
          </Link>
          <div className="mt-2 flex flex-wrap items-center gap-3">
            <h1 className="truncate text-2xl font-semibold tracking-tight text-slate-100">
              {caseItem.title}
            </h1>
            <Badge className={status.className}>{status.label}</Badge>
          </div>
          <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1 font-mono">
              <Hash className="h-3 w-3" />
              {caseItem.case_number}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {formatDateTime(caseItem.created_at)}
            </span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => setEditOpen(true)}>
            <Pencil className="h-4 w-4" /> Editar
          </Button>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="h-4 w-4" /> Eliminar
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} active={tab} onChange={setTab} />

      {/* Tab content */}
      <div className="animate-fade-in">
        {tab === 'overview' && <OverviewTab caseItem={caseItem} />}
        {tab === 'chrono' && <EventsTab caseId={caseItem.id} />}
        {tab === 'evidence' && <EvidenceTab caseId={caseItem.id} />}
        {tab === 'entities' && <EntitiesTab caseId={caseItem.id} />}
        {tab === 'graph' && <NexusGraphTab caseId={caseItem.id} />}
      </div>

      <CaseFormModal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSaved={async () => {
          setEditOpen(false)
          await load()
        }}
        initial={caseItem}
      />

      <ConfirmDialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={handleDelete}
        loading={deleting}
        title="Eliminar caso"
        message={`¿Eliminar el caso "${caseItem.case_number}"? Se borrarán sus eventos, evidencias y entidades asociadas. Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar caso"
      />
    </div>
  )
}

// ============================================================
// OVERVIEW TAB
// ============================================================
function OverviewTab({ caseItem }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-2">
        <CardHeader title="Descripción del caso" />
        <div className="p-5">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
            {caseItem.description || (
              <span className="italic text-slate-500">Sin descripción.</span>
            )}
          </p>
        </div>
      </Card>

      <Card>
        <CardHeader title="Metadatos" />
        <dl className="divide-y divide-slate-800">
          <MetaRow label="ID interno" value={`#${caseItem.id}`} mono />
          <MetaRow label="Estado" value={caseItem.status} />
          <MetaRow label="Creado" value={formatDateTime(caseItem.created_at)} />
          <MetaRow
            label="Actualizado"
            value={formatDateTime(caseItem.updated_at) || '—'}
          />
        </dl>
      </Card>
    </div>
  )
}

function MetaRow({ label, value, mono = false }) {
  return (
    <div className="flex items-center justify-between px-5 py-3 text-sm">
      <dt className="text-xs uppercase tracking-wider text-slate-500">{label}</dt>
      <dd className={`text-slate-200 ${mono ? 'font-mono text-xs' : ''}`}>
        {value}
      </dd>
    </div>
  )
}
