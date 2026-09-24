import { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import {
  Network, LayoutGrid, Circle, Share2, RefreshCw, Info,
} from 'lucide-react'
import { nexusApi } from '../../api/client'
import { Button, Card, Spinner, ErrorBanner, EmptyState } from '../ui'

const NODE_STYLE_BY_TYPE = {
  PERSON:       { 'background-color': '#0891b2', shape: 'ellipse' },
  PHONE:        { 'background-color': '#7c3aed', shape: 'round-rectangle' },
  EMAIL:        { 'background-color': '#6366f1', shape: 'round-rectangle' },
  VEHICLE:      { 'background-color': '#d97706', shape: 'diamond' },
  LOCATION:     { 'background-color': '#059669', shape: 'hexagon' },
  ADDRESS:      { 'background-color': '#059669', shape: 'hexagon' },
  ORGANIZATION: { 'background-color': '#e11d48', shape: 'rectangle' },
  ACCOUNT:      { 'background-color': '#0284c7', shape: 'round-rectangle' },
  DOCUMENT:     { 'background-color': '#64748b', shape: 'rectangle' },
  DEVICE:       { 'background-color': '#0d9488', shape: 'round-rectangle' },
  OTHER:        { 'background-color': '#475569', shape: 'ellipse' },
}

const LAYOUTS = [
  { id: 'cose', label: 'Fuerza', icon: Share2 },
  { id: 'circle', label: 'Circular', icon: Circle },
  { id: 'grid', label: 'Cuadrícula', icon: LayoutGrid },
]

export default function NexusGraphTab({ caseId }) {
  const containerRef = useRef(null)
  const cyRef = useRef(null)
  const [graph, setGraph] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [layoutName, setLayoutName] = useState('cose')
  const [selected, setSelected] = useState(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setGraph(await nexusApi.graph(caseId))
    } catch (err) {
      setError(err.userMessage || 'Error al cargar el grafo')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() /* eslint-disable-next-line */ }, [caseId])

  useEffect(() => {
    if (!containerRef.current || !graph) return

    const elements = [
      ...graph.nodes,
      ...graph.edges,
    ]

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'color': '#e2e8f0',
            'font-size': 11,
            'font-family': 'Inter, system-ui, sans-serif',
            'text-valign': 'bottom',
            'text-margin-y': 6,
            'text-outline-color': '#020617',
            'text-outline-width': 2,
            'border-width': 2,
            'border-color': '#0f172a',
            'width': 34,
            'height': 34,
            'transition-property': 'background-color, border-color',
            'transition-duration': '120ms',
          },
        },
        ...Object.entries(NODE_STYLE_BY_TYPE).map(([type, style]) => ({
          selector: `node[type="${type}"]`,
          style,
        })),
        {
          selector: 'node:selected',
          style: {
            'border-color': '#22d3ee',
            'border-width': 3,
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 1.5,
            'line-color': '#334155',
            'target-arrow-color': '#334155',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 0.8,
            'label': 'data(label)',
            'font-size': 9,
            'color': '#94a3b8',
            'text-rotation': 'autorotate',
            'text-background-color': '#020617',
            'text-background-opacity': 0.85,
            'text-background-padding': 3,
            'text-background-shape': 'roundrectangle',
            'opacity': 0.85,
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#22d3ee',
            'target-arrow-color': '#22d3ee',
            'width': 2.5,
            'opacity': 1,
          },
        },
      ],
      layout: { name: layoutName, animate: false, padding: 40 },
    })

    cy.on('tap', 'node', (evt) => {
      const d = evt.target.data()
      setSelected({ kind: 'node', ...d })
    })
    cy.on('tap', 'edge', (evt) => {
      const d = evt.target.data()
      setSelected({ kind: 'edge', ...d })
    })
    cy.on('tap', (evt) => {
      if (evt.target === cy) setSelected(null)
    })

    cyRef.current = cy
    return () => {
      cy.destroy()
      cyRef.current = null
    }
  }, [graph, layoutName])

  function fit() {
    cyRef.current?.fit(undefined, 40)
  }

  const isEmpty = graph && graph.nodes.length === 0

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-200">Grafo NEXUS</h2>
          <p className="text-xs text-slate-500">
            {graph
              ? `${graph.nodes.length} nodos · ${graph.edges.length} aristas`
              : 'Visualización de entidades y relaciones'}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <div className="flex rounded-md border border-slate-800 p-0.5">
            {LAYOUTS.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setLayoutName(id)}
                className={`flex items-center gap-1.5 rounded px-2.5 py-1.5 text-xs font-medium transition-colors ${
                  layoutName === id
                    ? 'bg-cyan-500/15 text-cyan-300'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Icon className="h-3.5 w-3.5" /> {label}
              </button>
            ))}
          </div>
          <Button variant="secondary" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Recargar
          </Button>
          <Button variant="secondary" size="sm" onClick={fit} disabled={!graph}>
            Ajustar
          </Button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      {loading ? (
        <Card>
          <Spinner label="Cargando grafo…" />
        </Card>
      ) : isEmpty ? (
        <Card>
          <EmptyState
            icon={Network}
            title="Sin entidades en el grafo"
            description="Añade entidades en la pestaña Entidades para visualizarlas aquí."
          />
        </Card>
      ) : (
        <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
          <Card className="relative overflow-hidden">
            <div
              ref={containerRef}
              className="h-[600px] w-full bg-slate-950/40"
            />
            <div className="pointer-events-none absolute bottom-3 left-3 flex items-center gap-1.5 rounded-md bg-slate-900/80 px-2 py-1 text-[10px] text-slate-400 backdrop-blur">
              <Info className="h-3 w-3" /> Click en nodos/aristas para ver detalles
            </div>
          </Card>

          <Card className="h-fit">
            <div className="border-b border-slate-800 px-4 py-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Detalles
              </h3>
            </div>
            <div className="p-4 text-sm">
              {!selected ? (
                <p className="text-xs text-slate-500">
                  Selecciona un elemento del grafo para ver su información.
                </p>
              ) : selected.kind === 'node' ? (
                <NodeDetails data={selected} />
              ) : (
                <EdgeDetails data={selected} />
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

function NodeDetails({ data }) {
  return (
    <dl className="space-y-3 text-xs">
      <Row label="Nombre" value={data.label} />
      <Row label="Tipo" value={data.type} />
      {data.identifier && <Row label="Identificador" value={data.identifier} mono />}
      {data.description && <Row label="Descripción" value={data.description} />}
      <Row label="ID" value={`e${data.entity_id}`} mono />
    </dl>
  )
}

function EdgeDetails({ data }) {
  return (
    <dl className="space-y-3 text-xs">
      <Row label="Tipo" value={data.type} />
      {data.description && <Row label="Descripción" value={data.description} />}
      {data.confidence != null && (
        <Row label="Confianza" value={String(data.confidence)} />
      )}
      <Row label="Origen → Destino" value={`${data.source} → ${data.target}`} mono />
    </dl>
  )
}

function Row({ label, value, mono = false }) {
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </dt>
      <dd
        className={`mt-0.5 break-words text-slate-200 ${
          mono ? 'font-mono text-[11px]' : ''
        }`}
      >
        {value}
      </dd>
    </div>
  )
}
