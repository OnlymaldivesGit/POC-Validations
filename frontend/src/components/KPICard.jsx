import { Info } from 'lucide-react'
import { cn } from '../lib/utils'
import Tooltip from './Tooltip'

const variants = {
  default: { wrap: 'glass-card border-l-4 border-l-slate-300', icon: 'bg-slate-100 text-slate-500' },
  red:     { wrap: 'glass-card kpi-red',   icon: 'bg-red-100 text-danger' },
  green:   { wrap: 'glass-card kpi-green', icon: 'bg-green-100 text-success' },
  amber:   { wrap: 'glass-card kpi-amber', icon: 'bg-amber-100 text-warning' },
}

export default function KPICard({ title, value, subtitle, icon: Icon, variant = 'default', onClick, tooltip }) {
  const v = variants[variant] || variants.default
  return (
    <div
      onClick={onClick}
      className={cn(v.wrap, 'p-5 relative overflow-hidden', onClick && 'cursor-pointer hover:scale-[1.02]')}
    >
      {Icon && (
        <div className={cn('absolute top-4 right-4 w-8 h-8 rounded-lg flex items-center justify-center', v.icon)}>
          <Icon className="w-4 h-4" />
        </div>
      )}
      <div className="flex items-center gap-1 mb-1 pr-10">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
        {tooltip && (
          <Tooltip content={tooltip}>
            <Info className="w-3 h-3 text-slate-400 cursor-help" />
          </Tooltip>
        )}
      </div>
      <p className="text-3xl font-bold text-slate-800 leading-none">{value ?? '—'}</p>
      {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
    </div>
  )
}
