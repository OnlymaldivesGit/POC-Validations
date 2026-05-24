import { useState } from 'react'
import { X } from 'lucide-react'
import { useRunHistory, useVendors, downloadExcel, downloadHtml } from '../services/api'
import RunCard from '../components/RunCard'

const PER_PAGE = 12

export default function Reports() {
  const [filters, setFilters] = useState({
    date_from: '', date_to: '', status: '', vendors: [],
  })
  const [page, setPage]       = useState(1)
  const [viewHtml, setViewHtml] = useState(null)

  const { data: vendorData } = useVendors()
  const vendors = vendorData?.vendors ?? []

  const apiFilters = {
    ...(filters.date_from && { date_from: filters.date_from }),
    ...(filters.date_to   && { date_to:   filters.date_to }),
    ...(filters.status    && { status:    filters.status }),
    ...(filters.vendors.length === 1 && { vendor: filters.vendors[0] }),
    page,
    per_page: PER_PAGE,
  }

  const { data, isLoading } = useRunHistory(apiFilters)
  const runs  = data?.runs  ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / PER_PAGE))

  function toggleVendor(name) {
    setFilters(f => ({
      ...f,
      vendors: f.vendors.includes(name)
        ? f.vendors.filter(v => v !== name)
        : [...f.vendors, name],
    }))
    setPage(1)
  }

  function clearFilters() {
    setFilters({ date_from: '', date_to: '', status: '', vendors: [] })
    setPage(1)
  }

  async function handleView(runId) {
    const html = await downloadHtml(runId)
    setViewHtml(html)
  }

  return (
    <div className="flex h-full">
      {/* Filter sidebar */}
      <aside className="w-56 flex-shrink-0 bg-white border-r border-slate-200 p-5 space-y-6 overflow-y-auto">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-slate-800 text-sm">Filters</h2>
          <button onClick={clearFilters} className="text-xs text-brand hover:underline">Clear</button>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Date From</p>
          <input
            type="date"
            value={filters.date_from}
            onChange={e => { setFilters(f => ({ ...f, date_from: e.target.value })); setPage(1) }}
            className="input-field text-xs"
          />
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Date To</p>
          <input
            type="date"
            value={filters.date_to}
            onChange={e => { setFilters(f => ({ ...f, date_to: e.target.value })); setPage(1) }}
            className="input-field text-xs"
          />
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Status</p>
          {['', 'complete', 'failed'].map(s => (
            <label key={s} className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer">
              <input
                type="radio"
                name="status"
                value={s}
                checked={filters.status === s}
                onChange={() => { setFilters(f => ({ ...f, status: s })); setPage(1) }}
                className="accent-brand"
              />
              {s || 'All'}
            </label>
          ))}
        </div>

        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Vendors</p>
          {vendors.map(v => (
            <label key={v.id} className="flex items-center gap-2 text-xs text-slate-600 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.vendors.includes(v.name)}
                onChange={() => toggleVendor(v.name)}
                className="accent-brand"
              />
              {v.name}
            </label>
          ))}
        </div>
      </aside>

      {/* Main area */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="page-title">Reports</h1>
          <span className="text-sm text-slate-400">{total} run{total !== 1 ? 's' : ''}</span>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 gap-4">
            {[0,1,2,3].map(i => (
              <div key={i} className="animate-pulse bg-slate-200 rounded-xl h-48" />
            ))}
          </div>
        ) : runs.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <p className="text-lg font-medium">No runs match your filters</p>
            <button onClick={clearFilters} className="text-sm text-brand hover:underline mt-2">Clear filters</button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {runs.map(run => (
                <RunCard
                  key={run.run_id}
                  run={run}
                  onView={() => handleView(run.run_id)}
                  onDownloadExcel={() => downloadExcel(run.run_id)}
                  onDownloadHtml={() => handleView(run.run_id)}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="flex justify-center gap-3 mt-8">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn-ghost disabled:opacity-40"
                >
                  ← Prev
                </button>
                <span className="text-sm text-slate-500 self-center">
                  Page {page} of {totalPages}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="btn-ghost disabled:opacity-40"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* HTML report modal */}
      {viewHtml && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Validation Report</h2>
              <button onClick={() => setViewHtml(null)} className="btn-ghost flex items-center gap-1.5">
                <X className="w-4 h-4" /> Close
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe
                srcDoc={viewHtml}
                title="Validation Report"
                className="w-full h-full border-0"
                sandbox="allow-scripts"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
