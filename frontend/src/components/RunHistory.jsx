import { useState } from 'react'
import { format, parseISO } from 'date-fns'
import { Eye, ChevronDown } from 'lucide-react'

export default function RunHistory({ runs = [], onSelectRun, activeRunId }) {
  const [showAll, setShowAll] = useState(false)
  const displayed = showAll ? runs : runs.slice(0, 5)

  if (!runs.length) {
    return <p className="text-xs text-slate-400 py-2">No previous runs</p>
  }

  return (
    <div className="space-y-1.5">
      {displayed.map(run => (
        <div
          key={run.run_id}
          className={`flex items-center justify-between px-3 py-2 rounded-lg border text-xs transition-colors ${
            activeRunId === run.run_id
              ? 'bg-brand/10 border-brand/30'
              : 'bg-white border-slate-200 hover:bg-slate-50'
          }`}
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              (run.total_violations ?? 0) > 0 ? 'bg-danger' : 'bg-success'
            }`} />
            <span className="text-slate-500">
              {run.timestamp ? format(parseISO(run.timestamp), 'MMM d, HH:mm') : '—'}
            </span>
            {run.triggered_by && (
              <span className="text-slate-400">by {run.triggered_by}</span>
            )}
            <span className={`font-semibold ${(run.total_violations ?? 0) > 0 ? 'text-danger' : 'text-success'}`}>
              {run.total_violations ?? 0} violations
            </span>
          </div>
          <button
            onClick={() => onSelectRun(run.run_id)}
            className="btn-ghost py-0.5 px-2 text-xs ml-2 flex-shrink-0"
          >
            <Eye className="w-3 h-3" /> View
          </button>
        </div>
      ))}
      {runs.length > 5 && (
        <button
          onClick={() => setShowAll(s => !s)}
          className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 transition-colors"
        >
          <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showAll ? 'rotate-180' : ''}`} />
          {showAll ? 'Show less' : `Show all ${runs.length} runs`}
        </button>
      )}
    </div>
  )
}
