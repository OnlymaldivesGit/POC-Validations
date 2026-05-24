import { format, parseISO } from 'date-fns'
import { Download, Eye, FileCode2 } from 'lucide-react'
import StatusBadge from './StatusBadge'

export default function RunCard({ run, onView, onDownloadExcel, onDownloadHtml }) {
  const ts = run.timestamp ? format(parseISO(run.timestamp), 'MMM d, yyyy HH:mm') : '—'
  const hasViolations = (run.total_violations ?? 0) > 0

  return (
    <div className="glass-card p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xl font-bold text-slate-800">{run.date}</p>
          <p className="text-xs text-slate-400 mt-0.5">{ts}</p>
        </div>
        <span className="badge-info text-xs">{run.vendor}</span>
      </div>

      <div className="flex items-center gap-3">
        <div className={`text-2xl font-bold ${hasViolations ? 'text-danger' : 'text-success'}`}>
          {run.total_violations ?? 0}
        </div>
        <div>
          <p className="text-xs text-slate-500">violations</p>
          <StatusBadge status={run.status} />
        </div>
      </div>

      <div className="flex gap-2 pt-2 border-t border-slate-100">
        <button onClick={onView}          className="btn-primary flex-1 flex items-center justify-center gap-1.5 text-xs py-1.5">
          <Eye className="w-3.5 h-3.5" /> View
        </button>
        <button onClick={onDownloadExcel} className="btn-outline flex items-center gap-1.5 text-xs py-1.5 px-3">
          <Download className="w-3.5 h-3.5" /> Excel
        </button>
        <button onClick={onDownloadHtml}  className="btn-ghost flex items-center gap-1.5 text-xs py-1.5">
          <FileCode2 className="w-3.5 h-3.5" /> HTML
        </button>
      </div>
    </div>
  )
}
