import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus, Search, FolderSearch, ArrowRight, Calendar, Hash,
} from 'lucide-react'
import { casesApi } from '../api/client'
import {
  Button, Card, EmptyState, ErrorBanner, Spinner, Badge,
} from '../components/ui'
import { CASE_STATUS, formatDateTime } from '../lib/format'
import CaseFormModal from '../components/cases/CaseFormModal'

export default function CasesList() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [createOpen, setCreateOpen] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const data = await casesApi.list()
      setCases(data)
    } catch (err) {
      setError(err.userMessage || 'Error al cargar los casos')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return cases.filter((c) => {
      if (statusFilter !== 'ALL' && c.status !== statusFilter) return false
      if (!q) return true
      return (
        c.case_number.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q) ||
        (c.description || '').toLowerCase().includes(q)
      )
    })
  }, [cases, query, statusFilter])

  async function handleCreated() {
    setCreateOpen(false)
    await load()
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-100">
            Casos
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Gestiona investigaciones, evidencias y análisis de entidades.
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" />
          Nuevo caso
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar por número, título o descripción…"
              className="input pl-9"
            />
          </div>
          <div className="flex gap-1 overflow-x-auto">
            {[
              { value: 'ALL', label: 'Todos' },
              ...Object.entries(CASE_STATUS).map(([v, { label }]) => ({
                value: v, label,
              })),
            ].map((opt) => (
              <button
                key={opt.value}
                onClick={() => setStatusFilter(opt.value)}
                className={`whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  statusFilter === opt.value
                    ? 'bg-cyan-500/15 text-cyan-300'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {/* List */}
      {loading ? (
        <Spinner label="Cargando casos…" />
      ) : filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={FolderSearch}
            title={cases.length === 0 ? 'No hay casos todavía' : 'Sin resultados'}
            description={
              cases.length === 0
                ? 'Crea tu primer caso para comenzar una investigación.'
                : 'Ajusta los filtros o la búsqueda.'
            }
            action={
              cases.length === 0 ? (
                <Button onClick={() => setCreateOpen(true)}>
                  <Plus className="h-4 w-4" /> Crear caso
                </Button>
              ) : null
            }
          />
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((c) => (
            <CaseCard key={c.id} caseItem={c} />
          ))}
        </div>
      )}

      <CaseFormModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onSaved={handleCreated}
      />
    </div>
  )
}

function CaseCard({ caseItem }) {
  const status = CASE_STATUS[caseItem.status] || CASE_STATUS.OPEN
  return (
    <Link
      to={`/cases/${caseItem.id}`}
      className="card group flex flex-col p-5 transition-colors hover:border-cyan-500/50 hover:bg-slate-900"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Hash className="h-3 w-3" />
          <span className="font-mono">{caseItem.case_number}</span>
        </div>
        <Badge className={status.className}>{status.label}</Badge>
      </div>

      <h3 className="mt-3 line-clamp-2 text-base font-semibold text-slate-100 group-hover:text-cyan-300">
        {caseItem.title}
      </h3>
      {caseItem.description && (
        <p className="mt-1.5 line-clamp-2 text-xs text-slate-400">
          {caseItem.description}
        </p>
      )}

      <div className="mt-4 flex items-center justify-between border-t border-slate-800 pt-3 text-[11px] text-slate-500">
        <span className="flex items-center gap-1.5">
          <Calendar className="h-3 w-3" />
          {formatDateTime(caseItem.created_at)}
        </span>
        <span className="flex items-center gap-1 font-medium text-slate-400 group-hover:text-cyan-300">
          Abrir
          <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
        </span>
      </div>
    </Link>
  )
}
