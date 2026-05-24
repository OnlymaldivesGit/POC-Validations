import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, BarChart, Bar, ResponsiveContainer,
} from 'recharts'
import { format, parseISO, isThisWeek } from 'date-fns'
import { PlayCircle, BarChart2, TrendingUp } from 'lucide-react'
import { useRunHistory, useVendors, downloadExcel, downloadHtml } from '../services/api'
import KPICard from '../components/KPICard'
import RunCard from '../components/RunCard'

const VENDOR_COLORS = ['#6366F1', '#F59E0B', '#22C55E', '#EF4444', '#8B5CF6', '#06B6D4']

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-slate-200 rounded-lg ${className}`} />
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [viewRun, setViewRun] = useState(null)

  const { data: histData, isLoading: histLoading } = useRunHistory({ per_page: 200 })
  const { data: vendorData, isLoading: vendorsLoading } = useRunHistory({ per_page: 10 })
  const { data: vendors }  = useVendors()

  const runs = histData?.runs ?? []
  const isLoading = histLoading || vendorsLoading

  const totalRuns   = histData?.total ?? 0
  const thisWeek    = runs.filter(r => r.timestamp && isThisWeek(parseISO(r.timestamp))).length
  const activeVendors = vendors?.vendors?.filter(v => v.active).length ?? 0
  const lastRun     = runs[0]?.date ?? '—'

  // Line chart: total_violations over time per vendor
  const uniqueVendors = [...new Set(runs.map(r => r.vendor))]
  const byDate = {}
  runs.forEach(r => {
    const d = r.date
    if (!byDate[d]) byDate[d] = { date: d }
    byDate[d][r.vendor] = (byDate[d][r.vendor] ?? 0) + (r.total_violations ?? 0)
  })
  const lineData = Object.values(byDate).sort((a, b) => a.date.localeCompare(b.date)).slice(-30)

  // Bar chart: average violations by category per vendor
  const vendorStats = {}
  runs.forEach(r => {
    if (!vendorStats[r.vendor]) vendorStats[r.vendor] = { vendor: r.vendor, count: 0, total: 0 }
    vendorStats[r.vendor].total += r.total_violations ?? 0
    vendorStats[r.vendor].count += 1
  })
  const barData = Object.values(vendorStats).map(v => ({
    vendor: v.vendor,
    avg_violations: v.count ? Math.round(v.total / v.count) : 0,
  }))

  const recent10 = runs.slice(0, 10)

  async function handleHtmlView(runId) {
    const html = await downloadHtml(runId)
    setViewRun(html)
  }

  if (!isLoading && runs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[60vh] gap-4">
        <BarChart2 className="w-16 h-16 text-slate-300" />
        <h2 className="text-xl font-semibold text-slate-600">No runs yet</h2>
        <p className="text-slate-400 text-sm">Run your first validation to see the dashboard.</p>
        <button onClick={() => navigate('/run')} className="btn-primary flex items-center gap-2">
          <PlayCircle className="w-4 h-4" /> Run Validation
        </button>
      </div>
    )
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="page-title">Dashboard</h1>
        <p className="text-xs text-slate-400">
          Last updated {runs[0]?.timestamp ? format(parseISO(runs[0].timestamp), 'MMM d HH:mm') : '—'}
        </p>
      </div>

      {/* Top KPIs */}
      {isLoading ? (
        <div className="grid grid-cols-4 gap-4">
          {[0,1,2,3].map(i => <Skeleton key={i} className="h-28" />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Total Runs"      value={totalRuns}    icon={BarChart2} variant="default" />
          <KPICard title="This Week"       value={thisWeek}     icon={TrendingUp} variant="default" />
          <KPICard title="Active Vendors"  value={activeVendors} icon={PlayCircle} variant="default" />
          <KPICard title="Last Run Date"   value={lastRun}      icon={BarChart2} variant="default" />
        </div>
      )}

      {/* Recent runs */}
      <section>
        <h2 className="section-title">Recent Runs</h2>
        {isLoading ? (
          <div className="grid grid-cols-2 gap-4">
            {[0,1,2,3].map(i => <Skeleton key={i} className="h-48" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {recent10.map(run => (
              <RunCard
                key={run.run_id}
                run={run}
                onView={() => handleHtmlView(run.run_id)}
                onDownloadExcel={() => downloadExcel(run.run_id)}
                onDownloadHtml={() => handleHtmlView(run.run_id)}
              />
            ))}
          </div>
        )}
      </section>

      {/* Charts */}
      {!isLoading && runs.length > 0 && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="glass-card p-6">
            <h2 className="section-title">Violations Over Time</h2>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={lineData} margin={{ left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                {uniqueVendors.map((v, i) => (
                  <Line
                    key={v}
                    type="monotone"
                    dataKey={v}
                    stroke={VENDOR_COLORS[i % VENDOR_COLORS.length]}
                    dot={false}
                    strokeWidth={2}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="glass-card p-6">
            <h2 className="section-title">Avg Violations by Vendor</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={barData} margin={{ left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="vendor" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="avg_violations" fill="#6366F1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* HTML report viewer modal */}
      {viewRun && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold text-slate-800">Validation Report</h2>
              <button onClick={() => setViewRun(null)} className="btn-ghost">✕ Close</button>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe
                srcDoc={viewRun}
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
