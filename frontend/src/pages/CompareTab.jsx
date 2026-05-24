import { useVendors, useRunHistory } from '../services/api'
import CompareTable from '../components/CompareTable'

export default function CompareTab({ date }) {
  const { data: vendorData } = useVendors()
  const vendors = vendorData?.vendors ?? []

  const { data: runsData } = useRunHistory({ date_from: date, date_to: date, per_page: 200 })
  const runs = runsData?.runs ?? []

  // For each vendor that has at least one run, take the latest
  const vendorResults = vendors
    .map(v => {
      const vRuns = runs
        .filter(r => r.vendor?.toLowerCase() === v.name?.toLowerCase())
        .sort((a, b) => b.timestamp?.localeCompare(a.timestamp ?? '') ?? 0)
      if (!vRuns.length) return null
      const latest = vRuns[0]
      return {
        vendorName: v.name,
        violationCounts: latest.violation_counts ?? {},
        totalViolations: latest.total_violations ?? 0,
        runId: latest.run_id,
        timestamp: latest.timestamp,
      }
    })
    .filter(Boolean)

  return (
    <div className="space-y-4">
      <CompareTable date={date} vendorResults={vendorResults} />
    </div>
  )
}
