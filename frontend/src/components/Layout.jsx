import { useState, useEffect } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { CalendarDays, BarChart3, Building2, Settings, Plane, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '../lib/utils'

const NAV = [
  { to: '/days',      label: 'Schedule Days', icon: CalendarDays },
  { to: '/analytics', label: 'Analytics',     icon: BarChart3 },
  { to: '/vendors',   label: 'Vendors',        icon: Building2 },
  { to: '/settings',  label: 'Settings',       icon: Settings },
]

function useBreadcrumb() {
  const { pathname } = useLocation()
  const parts = pathname.split('/').filter(Boolean)
  const crumbs = []
  if (parts[0] === 'days') {
    crumbs.push({ label: 'Schedule Days', to: '/days' })
    if (parts[1]) crumbs.push({ label: parts[1], to: `/days/${parts[1]}` })
    if (parts[2]) crumbs.push({ label: parts[2] === 'input' ? 'Input Data' : parts[2] === 'compare' ? 'Compare' : parts[2] })
  } else if (parts[0] === 'vendors') {
    crumbs.push({ label: 'Vendors' })
  } else if (parts[0] === 'analytics') {
    crumbs.push({ label: 'Analytics' })
  }
  return crumbs
}

export default function Layout() {
  const [collapsed, setCollapsed] = useState(
    () => localStorage.getItem('sidebar-collapsed') === 'true'
  )
  const crumbs = useBreadcrumb()

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', collapsed)
  }, [collapsed])

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className={cn(
        'flex-shrink-0 bg-sidebar flex flex-col transition-all duration-200',
        collapsed ? 'w-14' : 'w-60'
      )}>
        {/* Logo */}
        <div className={cn('px-3 py-5 border-b border-sidebar-border', collapsed ? 'flex justify-center' : '')}>
          {collapsed ? (
            <Plane className="w-5 h-5 text-brand-light" />
          ) : (
            <>
              <div className="flex items-center gap-2 mb-0.5">
                <Plane className="w-4 h-4 text-brand-light flex-shrink-0" />
                <span className="text-white font-bold text-sm tracking-tight">TMA Validator</span>
              </div>
              <p className="text-slate-500 text-xs ml-6">Crew Scheduling</p>
            </>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-3 space-y-0.5">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              title={collapsed ? label : undefined}
              className={({ isActive }) => cn(
                'flex items-center rounded-lg transition-all duration-150 text-sm font-medium group',
                collapsed ? 'justify-center p-2.5' : 'gap-3 px-3 py-2.5',
                isActive
                  ? 'bg-brand/20 text-white border-l-2 border-brand'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              )}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && label}
            </NavLink>
          ))}
        </nav>

        {/* Footer / collapse button */}
        <div className={cn('px-2 pb-4 pt-2 border-t border-sidebar-border', collapsed ? 'flex justify-center' : '')}>
          {!collapsed && (
            <p className="text-slate-500 text-xs px-3 mb-2">v2.0 · TMA</p>
          )}
          <button
            onClick={() => setCollapsed(c => !c)}
            className="flex items-center justify-center w-8 h-8 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 transition-colors mx-auto"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-12 bg-white border-b border-slate-200 flex items-center px-6 flex-shrink-0">
          <nav className="flex items-center gap-1.5 text-sm">
            {crumbs.map((c, i) => (
              <span key={i} className="flex items-center gap-1.5">
                {i > 0 && <span className="text-slate-300">/</span>}
                <span className={i === crumbs.length - 1 ? 'text-slate-700 font-medium' : 'text-slate-400'}>
                  {c.label}
                </span>
              </span>
            ))}
          </nav>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-surface">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
