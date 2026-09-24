import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { FolderSearch, Hexagon, Code2, Menu, X } from 'lucide-react'
import { useState } from 'react'

const NAV = [
  { to: '/cases', label: 'Casos', icon: FolderSearch },
]

export default function MainLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  const SidebarContent = (
    <>
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-cyan-500/15 text-cyan-400">
          <Hexagon className="h-5 w-5" strokeWidth={2.2} />
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold tracking-wide text-slate-100">
            NEXUS
          </p>
          <p className="text-[10px] uppercase tracking-widest text-slate-500">
            Forensic
          </p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-300'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-800 p-4 text-xs text-slate-500">
        <div className="flex items-center justify-between">
          <span>v0.1.0 · MVP</span>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="rounded p-1 hover:bg-slate-800 hover:text-slate-200"
            aria-label="Repositorio"
          >
            <Code2 className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </>
  )

  return (
    <div className="flex min-h-screen bg-slate-950">
      <aside className="hidden w-60 flex-col border-r border-slate-800 bg-slate-900/40 lg:flex">
        {SidebarContent}
      </aside>

      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="absolute inset-0 bg-slate-950/70"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative z-10 flex h-full w-64 flex-col border-r border-slate-800 bg-slate-900">
            {SidebarContent}
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-slate-800 bg-slate-900/40 px-4 py-3 lg:hidden">
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="rounded p-1 text-slate-400 hover:bg-slate-800"
            aria-label="Abrir menú"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <span className="text-sm font-semibold text-slate-200">
            NEXUS Forensic
          </span>
        </header>

        <main key={location.pathname} className="flex-1 overflow-x-hidden">
          <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
