import { clsx } from 'clsx'

const variants = {
  default: { border: 'border-l-slate-300', bg: '',           icon: 'bg-slate-100 text-slate-600' },
  red:     { border: 'border-l-danger',    bg: 'bg-red-50/60',   icon: 'bg-red-100 text-danger' },
  green:   { border: 'border-l-success',   bg: 'bg-green-50/60', icon: 'bg-green-100 text-success' },
  amber:   { border: 'border-l-warning',   bg: 'bg-amber-50/60', icon: 'bg-amber-100 text-warning' },
}

export default function KPICard({ title, value, subtitle, icon: Icon, variant = 'default', delta }) {
  const v = variants[variant] || variants.default
  return (
    <div className={clsx('glass-card p-5 border-l-4 relative overflow-hidden', v.border, v.bg)}>
      {Icon && (
        <div className={clsx('absolute top-4 right-4 w-9 h-9 rounded-lg flex items-center justify-center', v.icon)}>
          <Icon className="w-5 h-5" />
        </div>
      )}
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 pr-12">{title}</p>
      <p className="text-3xl font-bold text-slate-800 leading-none">{value ?? '—'}</p>
      {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      {delta && (
        <p className="text-xs font-medium text-slate-500 mt-2">{delta}</p>
      )}
    </div>
  )
}
