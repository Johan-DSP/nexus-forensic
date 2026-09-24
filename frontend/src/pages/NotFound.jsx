import { Link } from 'react-router-dom'
import { SearchX } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <SearchX className="h-10 w-10 text-slate-600" />
      <h1 className="text-2xl font-semibold text-slate-100">404</h1>
      <p className="text-sm text-slate-400">
        El recurso solicitado no existe o fue movido.
      </p>
      <Link to="/cases" className="btn btn-primary mt-2">
        Volver a Casos
      </Link>
    </div>
  )
}
