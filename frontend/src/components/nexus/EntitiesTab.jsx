import { useEffect, useMemo, useState } from 'react'
import {
  Plus, User, Phone, Car, Building2, MapPin, Link2, Trash2, Pencil, Network,
} from 'lucide-react'
import { nexusApi } from '../../api/client'
import {
  Button, Card, Spinner, ErrorBanner, EmptyState, Badge, ConfirmDialog,
} from '../ui'
import EntityFormModal from './EntityFormModal'
import RelationshipFormModal from './RelationshipFormModal'

const ENTITY_ICONS = {
  PERSON: User,
  PHONE: Phone,
  VEHICLE: Car,
  ORGANIZATION: Building2,
  LOCATION: MapPin,
  ADDRESS: MapPin,
}

const ENTITY_COLORS = {
  PERSON: 'text-cyan-400 bg-cyan-500/10',
  PHONE: 'text-violet-400 bg-violet-500/10',
  EMAIL: 'text-indigo-400 bg-indigo-500/10',
  VEHICLE: 'text-amber-400 bg-amber-500/10',
  LOCATION: 'text-emerald-400 bg-emerald-500/10',
  ADDRESS: 'text-emerald-400 bg-emerald-500/10',
  ORGANIZATION: 'text-rose-400 bg-rose-500/10',
  ACCOUNT: 'text-sky-400 bg-sky-500/10',
  DOCUMENT: 'text-slate-400 bg-slate-500/10',
  DEVICE: 'text-teal-400 bg-teal-500/10',
  OTHER: 'text-slate-400 bg-slate-500/10',
}

export default function EntitiesTab({ caseId }) {
  const [entities, setEntities] = useState([])
  const [relationships, setRelationships] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [entityFormOpen, setEntityFormOpen] = useState(false)
  const [editingEntity, setEditingEntity] = useState(null)

  const [relFormOpen, setRelFormOpen] = useState(false)
  const [editingRel, setEditingRel] = useState(null)

  const [deleting, setDeleting] = useState(null) // { kind: 'entity'|'rel', item }
  const [deleteLoading, setDeleteLoading] = useState(false)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [ents, rels] = await Promise.all([
        nexusApi.listEntities(caseId),
        nexusApi.listRelationships(caseId),
      ])
      setEntities(ents)
      setRelationships(rels)
    } catch (err) {
      setError(err.userMessage || 'Error al cargar entidades')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() /* eslint-disable-next-line */ }, [caseId])

  const entityById = useMemo(() => {
    const m = new Map()
    entities.forEach((e) => m.set(e.id, e))
    return m
  }, [entities])

  async function handleDelete() {
    if (!deleting) return
    setDeleteLoading(true)
    try {
      if (deleting.kind === 'entity') {
        await nexusApi.removeEntity(deleting.item.id)
      } else {
        await nexusApi.removeRelationship(deleting.item.id)
      }
      setDeleting(null)
      await load()
    } catch (err) {
      setError(err.userMessage || 'No se pudo eliminar')
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Entidades y relaciones</h2>
          <p className="text-xs text-slate-500">
            {entities.length} entidades · {relationships.length} relaciones
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => { setEditingRel(null); setRelFormOpen(true) }}
            disabled={entities.length < 2}
            title={entities.length < 2 ? 'Necesitas al menos 2 entidades' : ''}
          >
            <Link2 className="h-4 w-4" /> Nueva relación
          </Button>
          <Button onClick={() => { setEditingEntity(null); setEntityFormOpen(true) }}>
            <Plus className="h-4 w-4" /> Nueva entidad
          </Button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <Spinner label="Cargando entidades…" />
      ) : entities.length === 0 ? (
        <Card>
          <EmptyState
            icon={Network}
            title="Sin entidades registradas"
            description="Añade personas, vehículos, ubicaciones u organizaciones."
            action={
              <Button onClick={() => { setEditingEntity(null); setEntityFormOpen(true) }}>
                <Plus className="h-4 w-4" /> Añadir entidad
              </Button>
            }
          />
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Entities list */}
          <section>
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Entidades
            </h3>
            <ul className="space-y-2">
              {entities.map((e) => {
                const Icon = ENTITY_ICONS[e.type] || Network
                const colorCls = ENTITY_COLORS[e.type] || ENTITY_COLORS.OTHER
                return (
                  <li key={e.id}>
                    <Card className="flex items-center gap-3 p-3">
                      <div className={`flex h-9 w-9 items-center justify-center rounded-md ${colorCls}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-slate-100">
                          {e.name}
                        </p>
                        <p className="truncate text-[11px] text-slate-500">
                          {e.type}
                          {e.identifier && ` · ${e.identifier}`}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => { setEditingEntity(e); setEntityFormOpen(true) }}
                          aria-label="Editar"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost" size="sm"
                          onClick={() => setDeleting({ kind: 'entity', item: e })}
                          aria-label="Eliminar"
                        >
                          <Trash2 className="h-3.5 w-3.5 text-red-400" />
                        </Button>
                      </div>
                    </Card>
                  </li>
                )
              })}
            </ul>
          </section>

          {/* Relationships list */}
          <section>
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Relaciones
            </h3>
            {relationships.length === 0 ? (
              <Card className="p-4 text-xs text-slate-500">
                Sin relaciones todavía.
              </Card>
            ) : (
              <ul className="space-y-2">
                {relationships.map((r) => {
                  const src = entityById.get(r.source_entity_id)
                  const tgt = entityById.get(r.target_entity_id)
                  return (
                    <li key={r.id}>
                      <Card className="flex items-center gap-3 p-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex flex-wrap items-center gap-1.5 text-xs">
                            <span className="truncate font-medium text-slate-100">
                              {src?.name || `#${r.source_entity_id}`}
                            </span>
                            <Badge className="bg-slate-800 text-slate-300">
                              {r.relationship_type}
                            </Badge>
                            <span className="truncate font-medium text-slate-100">
                              {tgt?.name || `#${r.target_entity_id}`}
                            </span>
                          </div>
                          {r.description && (
                            <p className="mt-1 truncate text-[11px] text-slate-500">
                              {r.description}
                            </p>
                          )}
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost" size="sm"
                            onClick={() => { setEditingRel(r); setRelFormOpen(true) }}
                            aria-label="Editar"
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost" size="sm"
                            onClick={() => setDeleting({ kind: 'rel', item: r })}
                            aria-label="Eliminar"
                          >
                            <Trash2 className="h-3.5 w-3.5 text-red-400" />
                          </Button>
                        </div>
                      </Card>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>
        </div>
      )}

      <EntityFormModal
        open={entityFormOpen}
        onClose={() => setEntityFormOpen(false)}
        caseId={caseId}
        initial={editingEntity}
        onSaved={async () => { setEntityFormOpen(false); await load() }}
      />

      <RelationshipFormModal
        open={relFormOpen}
        onClose={() => setRelFormOpen(false)}
        caseId={caseId}
        entities={entities}
        initial={editingRel}
        onSaved={async () => { setRelFormOpen(false); await load() }}
      />

      <ConfirmDialog
        open={Boolean(deleting)}
        onClose={() => setDeleting(null)}
        onConfirm={handleDelete}
        loading={deleteLoading}
        title={deleting?.kind === 'entity' ? 'Eliminar entidad' : 'Eliminar relación'}
        message={
          deleting?.kind === 'entity'
            ? `¿Eliminar "${deleting.item.name}" y todas sus relaciones?`
            : '¿Eliminar esta relación?'
        }
      />
    </div>
  )
}
