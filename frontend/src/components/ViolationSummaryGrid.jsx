import {
  CalendarDays, Clock, Layers, Users,
  MoonStar, Plane, ArrowLeftRight, AlertTriangle,
} from 'lucide-react'
import KPICard from './KPICard'
import { format, parseISO } from 'date-fns'

const CATEGORIES = [
  { key: 'schedule_issues',   label: 'Schedule Issues',   icon: CalendarDays,   id: 'schedule',   tooltip: 'Flights missing from output vs input plan (C-1) or unassigned crew positions (C-2)' },
  { key: 'bh_violations',     label: 'BH Violations',     icon: Clock,          id: 'bh',         tooltip: 'Crew scheduled beyond 28-day (100h) or 365-day (1000h) block hour limits (C-9, C-10)' },
  { key: 'dh_violations',     label: 'DH Violations',     icon: Clock,          id: 'dh',         tooltip: 'Crew exceeding 28-day 210-hour duty time limit (C-11)' },
  { key: 'sector_violations', label: 'Sector Violations', icon: Layers,         id: 'sectors',    tooltip: 'Daily >14 sectors (C-14), weekly >48 (C-12), or >12-sector frequency rule (C-13)' },
  { key: 'pairing_issues',    label: 'Pairing Issues',    icon: Users,          id: 'pairing',    tooltip: 'Invalid seniority combinations (C-17), non-LTC with trainee (C-18), or wrong training pair (C-19)' },
  { key: 'status_issues',     label: 'Status Issues',     icon: AlertTriangle,  id: 'status',     tooltip: 'Leave crew scheduled (C-3), training crew at base flying (C-4), training outstation >1 flight (C-5)' },
  { key: 'overnight_issues',  label: 'Overnight Issues',  icon: MoonStar,       id: 'overnight',  tooltip: 'Starting airport mismatch (C-6) or crew ending outstation with leave next day (C-7)' },
  { key: 'aircraft_issues',   label: 'Aircraft Issues',   icon: Plane,          id: 'aircraft',   tooltip: 'Crew unqualified for assigned aircraft (C-8) or >1 aircraft swap per day (C-15)' },
]

export default function ViolationSummaryGrid({ violationCounts = {}, onCardClick, lastRunAt, lastRunBy }) {
  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {CATEGORIES.map(({ key, label, icon, id, tooltip }) => {
          const count = violationCounts[key] ?? 0
          return (
            <KPICard
              key={key}
              title={label}
              value={count}
              icon={icon}
              variant={count > 0 ? 'red' : 'green'}
              onClick={onCardClick ? () => onCardClick(id) : undefined}
              tooltip={tooltip}
            />
          )
        })}
      </div>
      {(lastRunAt || lastRunBy) && (
        <p className="text-xs text-slate-400 mt-2">
          {lastRunBy && `Run by ${lastRunBy}`}
          {lastRunBy && lastRunAt && ' · '}
          {lastRunAt && format(parseISO(lastRunAt), 'MMM d yyyy, HH:mm')}
        </p>
      )}
    </div>
  )
}
