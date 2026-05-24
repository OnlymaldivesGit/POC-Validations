import { NavLink, Outlet } from 'react-router-dom'
import {
  LayoutDashboard,
  PlayCircle,
  FileText,
  Settings,
  Plane,
} from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { to: '/dashboard', label: 'Dashboard',     icon: LayoutDashboard },
  { to: '/run',       label: 'Run Validator',  icon: PlayCircle },
  { to: '/reports',   label: 'Reports',        icon: FileText },
  { to: '/vendors',   label: 'Vendors',        icon: Settings },
]

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-60 flex-shrink-0 bg-sidebar flex flex-col">
        {/* Logo */}
        <div className="px-5 py-6 border-b border-white/10">
          <div className="flex items-center gap-2 mb-1">
            <Plane className="w-5 h-5 text-brand-light" />
            <span className="text-white font-bold text-base tracking-tight">TMA Validator</span>
          </div>
          <p className="text-slate-400 text-xs ml-7">Crew Scheduling</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-brand/20 text-white border-l-2 border-brand pl-2.5'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                )
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-white/10">
          <p className="text-slate-400 text-xs font-medium">v2.0</p>
          <p className="text-slate-400 text-xs">TMA · Corporate Strategy</p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-surface">
        <Outlet />
      </main>
    </div>
  )
}
