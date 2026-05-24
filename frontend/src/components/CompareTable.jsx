import { Download } from 'lucide-react'
import { downloadCompareCSV } from '../services/api'

const ROWS = [
  { key: 'schedule_issues',   label: 'Schedule Issues' },
  { key: 'bh_violations',     label: 'BH Violations' },
  { key: 'dh_violations',     label: 'DH Violations' },
  { key: 'sector_violations', label: 'Sector Violations' },
  { key: 'pairing_issues',    label: 'Pairing Issues' },
  { key: 'status_issues',     label: 'Status Issues' },
  { key: 'overnight_issues',  label: 'Overnight Issues' },
  { key: 'aircraft_issues',   label: 'Aircraft Issues' },
]

export default function CompareTable({ date, vendorResults = [] }) {
  if (vendorResults.length < 2) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <p className="text-sm">Run validation for at least 2 vendors to compare</p>
      </div>
    )
  }

  const totals = vendorResults.map(vr => ({
    vendor: vr.vendorName,
    total: ROWS.reduce((sum, r) => sum + (vr.violationCounts[r.key] ?? 0), 0),
  }))

  const minTotal = Math.min(...totals.map(t => t.total))
  const best = totals.filter(t => t.total === minTotal).map(t => t.vendor)

  // Build CSV data
  function exportCsv() {
    const rows = ROWS.map(row => {
      const entry = { Category: row.label }
      vendorResults.forEach(vr => { entry[vr.vendorName] = vr.violationCounts[row.key] ?? 0 })
      return entry
    })
    const totalRow = { Category: 'TOTAL' }
    vendorResults.forEach(vr => { totalRow[vr.vendorName] = ROWS.reduce((s, r) => s + (vr.violationCounts[r.key] ?? 0), 0) })
    rows.push(totalRow)
    downloadCompareCSV(date, rows)
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3 border-b border-slate-100">
        <h3 className="font-semibold text-slate-800">Vendor Comparison</h3>
        <button onClick={exportCsv} className="btn-ghost py-1 text-xs">
          <Download className="w-3.5 h-3.5" /> Export CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50">
              <th className="px-5 py-3 text-left font-semibold text-slate-600 w-48">Category</th>
              {vendorResults.map(vr => (
                <th key={vr.vendorName} className="px-4 py-3 text-center font-semibold text-slate-700">
                  {vr.vendorName}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map(row => {
              const vals = vendorResults.map(vr => vr.violationCounts[row.key] ?? 0)
              const min = Math.min(...vals), max = Math.max(...vals)
              return (
                <tr key={row.key} className="border-t border-slate-100">
                  <td className="px-5 py-2.5 text-slate-600 font-medium">{row.label}</td>
                  {vendorResults.map((vr, i) => {
                    const v = vals[i]
                    const isMin = v === min && min !== max
                    const isMax = v === max && min !== max
                    return (
                      <td key={vr.vendorName} className={`px-4 py-2.5 text-center font-semibold ${
                        v === 0 ? 'text-success' :
                        isMin   ? 'bg-green-100 text-green-800' :
                        isMax   ? 'bg-red-100 text-red-700' : 'text-slate-700'
                      }`}>
                        {v}
                      </td>
                    )
                  })}
                </tr>
              )
            })}

            {/* Total row */}
            <tr className="border-t-2 border-slate-200 bg-slate-50 font-bold">
              <td className="px-5 py-3 text-slate-800">TOTAL</td>
              {totals.map(t => (
                <td key={t.vendor} className={`px-4 py-3 text-center ${
                  t.total === minTotal ? 'text-success' : 'text-slate-800'
                }`}>
                  {t.total}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      <div className="px-5 py-3 border-t border-slate-100 text-xs text-slate-500">
        Best overall: <span className="font-semibold text-success">{best.join(', ')}</span>
      </div>
    </div>
  )
}
