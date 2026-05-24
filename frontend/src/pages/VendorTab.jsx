import { useState, useRef, useEffect } from 'react'
import { Loader2, Upload, Play, Download, FileCode2, Info } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import {
  PieChart, Pie, Cell, Tooltip as RechartsTip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from 'recharts'
import {
  useRunValidation, useVendorRuns, downloadExcel, downloadHtml,
} from '../services/api'
import ViolationSummaryGrid from '../components/ViolationSummaryGrid'
import ViolationAccordion from '../components/ViolationAccordion'
import ViolationTable from '../components/ViolationTable'
import AnalyticsChart from '../components/AnalyticsChart'
import RunHistory from '../components/RunHistory'

const PIE_COLORS = ['#6366F1', '#22C55E', '#F59E0B', '#EF4444']

const SUB_TABS = ['Block Hours', 'Sectors', 'Swaps']

function CompactSummary({ violationCounts, lastRunAt, lastRunBy }) {
  const cats = [
    { key: 'schedule_issues',   color: 'schedule' },
    { key: 'bh_violations',     color: 'bh' },
    { key: 'dh_violations',     color: 'dh' },
    { key: 'sector_violations', color: 'sectors' },
    { key: 'pairing_issues',    color: 'pairing' },
    { key: 'status_issues',     color: 'status' },
    { key: 'overnight_issues',  color: 'overnight' },
    { key: 'aircraft_issues',   color: 'aircraft' },
  ]
  return (
    <div className="flex items-center justify-between px-4 py-2">
      <div className="flex items-center gap-2 flex-wrap">
        {cats.map(({ key }) => {
          const count = violationCounts[key] ?? 0
          return (
            <span key={key} className={`flex items-center gap-1 text-xs font-semibold ${count > 0 ? 'text-danger' : 'text-success'}`}>
              <span className={`w-2 h-2 rounded-full ${count > 0 ? 'bg-danger' : 'bg-success'}`} />
              {count}
            </span>
          )
        })}
      </div>
      <span className="text-xs text-slate-400 flex-shrink-0 ml-4">
        {lastRunBy && `${lastRunBy} · `}{lastRunAt && format(parseISO(lastRunAt), 'MMM d HH:mm')}
      </span>
    </div>
  )
}

export default function VendorTab({ date, vendor }) {
  const [solverFile, setSolverFile] = useState(null)
  const [addedAt,    setAddedAt]    = useState(null)
  const [result,     setResult]     = useState(null) // live result from mutation
  const [viewRunId,  setViewRunId]  = useState(null) // for read-only historical view
  const [isSticky,   setIsSticky]   = useState(false)
  const [subTab,     setSubTab]     = useState(0)
  const [readOnly,   setReadOnly]   = useState(false)
  const [htmlView,   setHtmlView]   = useState(null)

  const sentinelRef = useRef(null)
  const runMut = useRunValidation()
  const { data: runs = [], refetch: refetchRuns } = useVendorRuns(date, vendor?.name)

  // IntersectionObserver for sticky summary
  useEffect(() => {
    if (!sentinelRef.current) return
    const obs = new IntersectionObserver(
      ([entry]) => setIsSticky(!entry.isIntersecting),
      { rootMargin: '-1px 0px 0px 0px' }
    )
    obs.observe(sentinelRef.current)
    return () => obs.disconnect()
  }, [result, viewRunId])

  function handleFilePick() {
    const input = document.createElement('input')
    input.type  = 'file'
    input.accept = '.xlsx,.xls'
    input.onchange = e => {
      const f = e.target.files[0]
      if (f) { setSolverFile(f); setAddedAt(new Date().toISOString()) }
    }
    input.click()
  }

  async function handleRun() {
    if (!solverFile || !vendor) return
    const r = await runMut.mutateAsync({ date, vendorId: vendor.id, files: [solverFile] })
    setResult(r)
    setReadOnly(false)
    setViewRunId(null)
    refetchRuns()
  }

  async function handleSelectRun(runId) {
    setViewRunId(runId)
    setReadOnly(true)
    // Load HTML for iframe display of historical run
    const html = await downloadHtml(runId)
    setHtmlView(html)
    setResult(null)
  }

  function backToLatest() {
    setReadOnly(false)
    setViewRunId(null)
    setHtmlView(null)
  }

  function scrollTo(id) {
    document.getElementById(`va-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  // Determine display state
  const hasResult    = !!result
  const latestRun    = runs[0]
  const displayCounts = result?.violation_counts ?? null

  // Analytics data from output_master in result
  const outputMaster = result?.output_master ?? []
  function chartData(crewType, metric) {
    const src = crewType ? outputMaster.filter(r => r['Crew Type'] === crewType) : outputMaster
    return src.map(r => ({ name: r['Crew code'], value: parseFloat(r[metric]) || 0 }))
  }

  // Swaps data
  const swapsCounts = [
    { name: 'Captain',        value: outputMaster.filter(r => r['Crew Type'] === 'Captain' && r['No. of swaps'] > 0).length },
    { name: 'First Officer',  value: outputMaster.filter(r => r['Crew Type'] === 'First Officer' && r['No. of swaps'] > 0).length },
    { name: 'Flight Attendant', value: outputMaster.filter(r => r['Crew Type'] === 'Flight Attendant' && r['No. of swaps'] > 0).length },
  ]
  const swapsBarData = outputMaster.filter(r => (r['No. of swaps'] ?? 0) > 0)
    .map(r => ({ name: r['Crew code'], value: r['No. of swaps'] }))
    .sort((a,b) => b.value - a.value)

  const v = result?.violations ?? {}

  // State A: no file
  if (!solverFile && !hasResult && !runs.length) return (
    <div className="flex flex-col items-center justify-center py-20 gap-5 text-center">
      <div className="w-16 h-16 bg-brand/10 rounded-2xl flex items-center justify-center">
        <Upload className="w-8 h-8 text-brand" />
      </div>
      <div>
        <h3 className="font-semibold text-slate-800 text-lg">Upload {vendor?.name} solver output</h3>
        <p className="text-sm text-slate-400 mt-1">to begin validation</p>
      </div>
      {vendor?.solver_output_columns && (
        <div className="text-xs text-slate-400 max-w-xs">
          Expected columns: {Object.values(vendor.solver_output_columns).join(', ')}
        </div>
      )}
      <button onClick={handleFilePick} className="btn-primary">
        <Upload className="w-4 h-4" /> Upload Solver Output
      </button>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Upload bar */}
      <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl">
        <div className="text-sm text-slate-600">
          {solverFile ? (
            <span><strong className="text-slate-800">{solverFile.name}</strong>
              <span className="ml-2 text-slate-400">· Added {addedAt ? format(parseISO(addedAt), 'HH:mm') : 'just now'}</span>
            </span>
          ) : latestRun ? (
            <span className="text-slate-400">No new output selected</span>
          ) : (
            <span className="text-slate-400">No solver output uploaded</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleFilePick} className="btn-ghost text-sm">
            <Upload className="w-4 h-4" /> Upload New Output
          </button>
          <button
            onClick={handleRun}
            disabled={!solverFile || runMut.isPending}
            className="btn-primary text-sm"
          >
            {runMut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run Validation
          </button>
        </div>
      </div>

      {/* State B: file selected but no result yet */}
      {solverFile && !hasResult && !runs.length && (
        <div className="flex flex-col items-center justify-center py-12 gap-4 text-center glass-card">
          <Info className="w-8 h-8 text-brand/50" />
          <p className="text-sm text-slate-500">Solver output ready. Run validation to see results.</p>
          <button onClick={handleRun} disabled={runMut.isPending} className="btn-primary">
            {runMut.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Run Validation
          </button>
        </div>
      )}

      {/* Read-only banner */}
      {readOnly && (
        <div className="flex items-center justify-between px-4 py-2 bg-amber-50 border border-amber-200 rounded-lg text-sm">
          <span className="text-amber-700">
            Viewing historical run {viewRunId ? viewRunId.slice(0, 8) : ''}
          </span>
          <button onClick={backToLatest} className="btn-ghost py-1 text-xs">← Back to latest</button>
        </div>
      )}

      {/* State C: live result */}
      {hasResult && !readOnly && (
        <>
          {/* Sentinel for sticky detection */}
          <div ref={sentinelRef} className="h-px" />

          {/* Sticky summary bar */}
          <div className={isSticky ? 'sticky top-0 z-20 bg-white border-b border-slate-200 shadow-sm rounded-none' : ''}>
            {isSticky ? (
              <CompactSummary
                violationCounts={displayCounts}
                lastRunAt={result.timestamp}
                lastRunBy={result.triggered_by}
              />
            ) : (
              <ViolationSummaryGrid
                violationCounts={displayCounts}
                onCardClick={scrollTo}
                lastRunAt={result.timestamp}
                lastRunBy={result.triggered_by}
              />
            )}
          </div>

          {/* Violations */}
          <div className="space-y-3">
            <ViolationAccordion id="va-schedule" category="Schedule Issues" ruleId="C-1, C-2" count={(v.schedule_check?.length ?? 0) + (v.unassigned_flights?.length ?? 0)}>
              <ViolationTable data={[...(v.schedule_check ?? []), ...(v.unassigned_flights ?? [])]} title="Schedule + Unassigned" />
            </ViolationAccordion>

            <ViolationAccordion id="va-bh" category="Block Hour Violations" ruleId="C-9, C-10" count={(v.block_hour_issue_1?.length ?? 0) + (v.block_hour_issue_2?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.block_hour_issue_1 ?? []} title="Ending at MLE" ruleId="C-9" highlightColumns={[{ key: 'Block hours', threshold: 0, comparator: 'gt' }]} />
                <ViolationTable data={v.block_hour_issue_2 ?? []} title="Ending at Outstation" ruleId="C-10" />
              </div>
            </ViolationAccordion>

            <ViolationAccordion id="va-dh" category="Duty Hour Violations" ruleId="C-11" count={v.duty_hour_issue?.length ?? 0}>
              <ViolationTable data={v.duty_hour_issue ?? []} emptyMessage="No duty hour violations" />
            </ViolationAccordion>

            <ViolationAccordion id="va-sectors" category="Sector Violations" ruleId="C-12, C-13, C-14" count={(v.sector_issue_1?.length ?? 0) + (v.sector_issue_2?.length ?? 0) + (v.daily_sector_violation?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.daily_sector_violation ?? []} title="Daily > 14 sectors" ruleId="C-14" />
                <ViolationTable data={v.sector_issue_1 ?? []} title="Weekly > 48 sectors" ruleId="C-12" />
                <ViolationTable data={v.sector_issue_2 ?? []} title="> 12 sectors frequency" ruleId="C-13" />
              </div>
            </ViolationAccordion>

            <ViolationAccordion id="va-pairing" category="Pairing Issues" ruleId="C-17, C-18, C-19" count={(v.pairings_issue_1?.length ?? 0) + (v.ltc_check?.length ?? 0) + (v.training_issue?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.pairings_issue_1 ?? []} title="Seniority violations" ruleId="C-17" />
                <ViolationTable data={v.ltc_check ?? []} title="LTC requirement" ruleId="C-18" />
                <ViolationTable data={v.training_issue ?? []} title="Training pairing" ruleId="C-19" />
              </div>
            </ViolationAccordion>

            <ViolationAccordion id="va-status" category="Status Issues" ruleId="C-3, C-4, C-5" count={(v.leaves_working?.length ?? 0) + (v.crew_mistake_1?.length ?? 0) + (v.crew_mistake_11?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.leaves_working ?? []} title="Leave crew scheduled" ruleId="C-3" />
                <ViolationTable data={v.crew_mistake_1 ?? []} title="Training at base flying" ruleId="C-4" />
                <ViolationTable data={v.crew_mistake_11 ?? []} title="Training outstation > 1 flight" ruleId="C-5" />
              </div>
            </ViolationAccordion>

            <ViolationAccordion id="va-overnight" category="Overnight Issues" ruleId="C-6, C-7" count={(v.crew_mistake_2?.length ?? 0) + (v.crew_mistake_3?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.crew_mistake_2 ?? []} title="Starting position mismatch" ruleId="C-6" />
                <ViolationTable data={v.crew_mistake_3 ?? []} title="Overnight on leave day" ruleId="C-7" />
              </div>
            </ViolationAccordion>

            <ViolationAccordion id="va-aircraft" category="Aircraft Issues" ruleId="C-8, C-15, C-16" count={(v.aircraft_issue?.length ?? 0) + (v.swaps_issue?.length ?? 0)}>
              <div className="space-y-3">
                <ViolationTable data={v.aircraft_issue ?? []} title="AC qualification" ruleId="C-8" />
                <ViolationTable data={v.swaps_issue ?? []} title="Swap count > 1" ruleId="C-15" />
                <ViolationTable data={v.short_time_diffs ?? []} title="Swap gap < 45 min" ruleId="C-16" />
              </div>
            </ViolationAccordion>
          </div>

          {/* Analytics */}
          {outputMaster.length > 0 && (
            <div className="glass-card overflow-hidden">
              <div className="flex border-b border-slate-200">
                {SUB_TABS.map((t, i) => (
                  <button key={t} onClick={() => setSubTab(i)}
                    className={`px-5 py-3 text-sm font-medium transition-colors ${
                      subTab === i ? 'bg-brand text-white' : 'text-slate-500 hover:bg-slate-50'
                    }`}>
                    {t}
                  </button>
                ))}
              </div>
              <div className="p-5 space-y-4">
                {subTab === 0 && (
                  <div className="grid grid-cols-2 gap-4">
                    <AnalyticsChart data={chartData(null, 'Block hours')} title="All Crew — Block Hours" unit=" h" color="#6366F1" />
                    <AnalyticsChart data={chartData('Captain', 'Block hours')} title="Captains" unit=" h" color="#8B5CF6" />
                    <AnalyticsChart data={chartData('First Officer', 'Block hours')} title="First Officers" unit=" h" color="#06B6D4" />
                    <AnalyticsChart data={chartData('Flight Attendant', 'Block hours')} title="Flight Attendants" unit=" h" color="#22C55E" />
                  </div>
                )}
                {subTab === 1 && (
                  <div className="grid grid-cols-2 gap-4">
                    <AnalyticsChart data={chartData(null, 'Total sectors')} title="All Crew — Sectors" color="#6366F1" />
                    <AnalyticsChart data={chartData('Captain', 'Total sectors')} title="Captains" color="#8B5CF6" />
                    <AnalyticsChart data={chartData('First Officer', 'Total sectors')} title="First Officers" color="#06B6D4" />
                    <AnalyticsChart data={chartData('Flight Attendant', 'Total sectors')} title="Flight Attendants" color="#22C55E" />
                  </div>
                )}
                {subTab === 2 && (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="glass-card p-4">
                      <h4 className="text-sm font-semibold text-slate-700 mb-3">Swaps by Crew Type</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie data={swapsCounts} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                            {swapsCounts.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                          </Pie>
                          <RechartsTip />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <AnalyticsChart data={swapsBarData} title="Crew with Aircraft Swaps" color="#F59E0B" />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Downloads + run history */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex gap-3">
              <button onClick={() => downloadExcel(result.run_id)} className="btn-outline text-sm">
                <Download className="w-4 h-4" /> Download Excel
              </button>
              <button onClick={async () => { const h = await downloadHtml(result.run_id); setHtmlView(h) }} className="btn-outline text-sm">
                <FileCode2 className="w-4 h-4" /> View HTML Report
              </button>
            </div>

            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
                Previous runs for {vendor?.name} on {date}
              </p>
              <RunHistory runs={runs} onSelectRun={handleSelectRun} activeRunId={viewRunId} />
            </div>
          </div>
        </>
      )}

      {/* Read-only: historical HTML view */}
      {readOnly && htmlView && (
        <div className="glass-card overflow-hidden">
          <iframe srcDoc={htmlView} title="Historical Report" className="w-full h-[800px] border-0" sandbox="allow-scripts" />
        </div>
      )}

      {/* Shows previous runs list even when no live result */}
      {!hasResult && runs.length > 0 && (
        <div className="glass-card p-5">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Previous runs for {vendor?.name} on {date}
          </p>
          <RunHistory runs={runs} onSelectRun={handleSelectRun} activeRunId={viewRunId} />
        </div>
      )}

      {/* HTML report modal */}
      {htmlView && !readOnly && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold">Validation Report</h2>
              <button onClick={() => setHtmlView(null)} className="btn-ghost">✕ Close</button>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe srcDoc={htmlView} title="Report" className="w-full h-full border-0" sandbox="allow-scripts" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
