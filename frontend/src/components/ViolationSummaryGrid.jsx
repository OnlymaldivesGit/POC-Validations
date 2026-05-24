import {
  CalendarDays, Clock, Layers, Users,
  MoonStar, Plane, ArrowLeftRight, AlertTriangle,
} from 'lucide-react'
import KPICard from './KPICard'

const CATEGORIES = [
  { key: 'schedule_issues',  label: 'Schedule Issues',   icon: CalendarDays },
  { key: 'bh_violations',    label: 'BH Violations',     icon: Clock },
  { key: 'dh_violations',    label: 'DH Violations',     icon: Clock },
  { key: 'sector_violations',label: 'Sector Violations', icon: Layers },
  { key: 'pairing_issues',   label: 'Pairing Issues',    icon: Users },
  { key: 'status_issues',    label: 'Status Issues',     icon: AlertTriangle },
  { key: 'overnight_issues', label: 'Overnight Issues',  icon: MoonStar },
  { key: 'aircraft_issues',  label: 'Aircraft Issues',   icon: Plane },
]

export default function ViolationSummaryGrid({ violationCounts = {} }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {CATEGORIES.map(({ key, label, icon }) => {
        const count = violationCounts[key] ?? 0
        return (
          <KPICard
            key={key}
            title={label}
            value={count}
            icon={icon}
            variant={count > 0 ? 'red' : 'green'}
          />
        )
      })}
    </div>
  )
}
