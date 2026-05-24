import { useState, useMemo } from 'react'
import { CheckCircle, ChevronUp, ChevronDown, Download, Search } from 'lucide-react'
import { toCsv, triggerDownload } from '../lib/utils'

const PAGE_SIZE = 20

function cellHighlight(row, col, highlightColumns) {
  if (!highlightColumns?.length) return ''
  const rule = highlightColumns.find(h => h.key === col)
  if (!rule) return ''
  const val = parseFloat(row[col])
  if (isNaN(val)) return ''
  const cmp = rule.comparator === 'lt' ? val < rule.threshold : val > rule.threshold
  return cmp ? 'bg-red-100 text-red-700' : ''
}

export default function ViolationTable({ data = [], title, ruleId, emptyMessage = 'No violations found', highlightColumns }) {
  const [sort, setSort]   = useState({ col: null, dir: 'asc' })
  const [search, setSrch] = useState('')
  const [page, setPage]   = useState(1)

  const columns = data.length ? Object.keys(data[0]) : []

  const filtered = useMemo(() => {
    if (!search.trim()) return data
    const q = search.toLowerCase()
    return data.filter(r => Object.values(r).some(v => String(v ?? '').toLowerCase().includes(q)))
  }, [data, search])

  const sorted = useMemo(() => {
    if (!sort.col) return filtered
    return [...filtered].sort((a, b) => {
      const av = a[sort.col] ?? '', bv = b[sort.col] ?? ''
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true })
      return sort.dir === 'asc' ? cmp : -cmp
    })
  }, [filtered, sort])

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE))
  const pageRows   = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  function toggleSort(col) {
    setSort(s => s.col === col ? { col, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { col, dir: 'asc' })
    setPage(1)
  }

  function exportCsv() {
    const blob = new Blob([toCsv(data)], { type: 'text/csv' })
    triggerDownload(blob, `${ruleId || title || 'violations'}.csv`)
  }

  if (!data.length) {
    return (
      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
        <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          {ruleId && <span className="badge-info">{ruleId}</span>}
          {title && <span className="font-semibold text-slate-800 text-sm">{title}</span>}
          <span className="badge-fail">{data.length}</span>
        </div>
        <button onClick={exportCsv} className="btn-ghost py-1 text-xs">
          <Download className="w-3.5 h-3.5" /> CSV
        </button>
      </div>

      <div className="px-4 py-2 border-b border-slate-100">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
          <input value={search} onChange={e => { setSrch(e.target.value); setPage(1) }}
            placeholder="Search…" className="input-field pl-8 py-1.5 text-xs" />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-50">
              {columns.map(col => (
                <th key={col} onClick={() => toggleSort(col)}
                  className="px-3 py-2.5 text-left font-semibold text-slate-600 cursor-pointer select-none whitespace-nowrap hover:bg-slate-100">
                  <div className="flex items-center gap-1">
                    {col}
                    {sort.col === col
                      ? sort.dir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />
                      : <ChevronUp className="w-3 h-3 opacity-0" />}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageRows.map((row, i) => (
              <tr key={i} className="border-t border-slate-100 hover:bg-slate-50">
                {columns.map(col => (
                  <td key={col} className={`px-3 py-2 whitespace-nowrap ${cellHighlight(row, col, highlightColumns)}`}>
                    {row[col] ?? '—'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-100 text-xs text-slate-500">
          <span>Showing {(page-1)*PAGE_SIZE+1}–{Math.min(page*PAGE_SIZE, sorted.length)} of {sorted.length}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(p => Math.max(1,p-1))} disabled={page===1} className="btn-ghost py-1 px-2 text-xs disabled:opacity-40">Prev</button>
            <button onClick={() => setPage(p => Math.min(totalPages,p+1))} disabled={page===totalPages} className="btn-ghost py-1 px-2 text-xs disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
