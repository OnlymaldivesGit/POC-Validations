import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, ChevronRight, Search, CalendarDays } from 'lucide-react'
import { format, parseISO, isToday, isYesterday } from 'date-fns'
import { useDays } from '../services/api'

function relLabel(dateStr) {
  try {
    const d = parseISO(dateStr)
    if (isToday(d))     return 'Today'
    if (isYesterday(d)) return 'Yesterday'
  } catch {}
  return null
}

function VendorPill({ vendor }) {
  if (vendor.status === 'clean') return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800">
      ✓ {vendor.name}
    </span>
  )
  if (vendor.status === 'violations') return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
      {vendor.violationCount} {vendor.name}
    </span>
  )
  if (vendor.status === 'uploaded') return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
      {vendor.name}
    </span>
  )
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border border-slate-300 text-slate-500">
      {vendor.name}
    </span>
  )
}

export default function ScheduleDays() {
  const navigate = useNavigate()
  const [search,  setSearch]  = useState('')
  const [filter,  setFilter]  = useState('all')
  const [newDate, setNewDate] = useState('')
  const [showPicker, setShowPicker] = useState(false)

  const { data: days = [], isLoading } = useDays()

  const filtered = days.filter(d => {
    if (search && !d.date.includes(search)) return false
    if (filter === 'input-ready' && (d.inputStatus?.count ?? 0) < (d.inputStatus?.total ?? 10)) return false
    if (filter === 'has-issues'  && !d.vendors?.some(v => v.status === 'violations')) return false
    return true
  })

  function goToDay(date) { navigate(`/days/${date}/input`) }

  function handleNewDay() {
    if (newDate) { navigate(`/days/${newDate}/input`); setShowPicker(false) }
  }

  return (
    <div className="p-8 space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Schedule Days</h1>
        <div className="flex items-center gap-2">
          {showPicker ? (
            <>
              <input type="date" value={newDate} onChange={e => setNewDate(e.target.value)}
                className="input-field max-w-[160px] text-sm" />
              <button onClick={handleNewDay} disabled={!newDate} className="btn-primary py-1.5 text-sm">Go</button>
              <button onClick={() => setShowPicker(false)} className="btn-ghost py-1.5 text-sm">Cancel</button>
            </>
          ) : (
            <button onClick={() => setShowPicker(true)} className="btn-primary">
              <Plus className="w-4 h-4" /> New Day
            </button>
          )}
        </div>
      </div>

      {/* Filter bar */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search date…" className="input-field pl-9" />
        </div>
        {['all', 'input-ready', 'has-issues'].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              filter === f ? 'bg-brand text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}>
            {f === 'all' ? 'All' : f === 'input-ready' ? 'Input Ready' : 'Has Issues'}
          </button>
        ))}
      </div>

      {/* List */}
      {isLoading ? (
        <div className="space-y-3">
          {[0,1,2,3,4].map(i => <div key={i} className="skeleton h-20 w-full" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <CalendarDays className="w-14 h-14 text-slate-200" />
          <p className="text-slate-400">No schedule days yet</p>
          <button onClick={() => setShowPicker(true)} className="btn-primary">
            <Plus className="w-4 h-4" /> Add your first day
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(day => {
            const rel  = relLabel(day.date)
            const dayName = (() => { try { return format(parseISO(day.date), 'EEEE') } catch { return '' } })()
            const inputCount = day.inputStatus?.count ?? 0
            const inputTotal = day.inputStatus?.total ?? 10

            return (
              <button
                key={day.date}
                onClick={() => goToDay(day.date)}
                className="glass-card w-full flex items-center justify-between px-5 py-4 text-left hover:shadow-glass-lg cursor-pointer"
              >
                {/* Date */}
                <div className="flex items-center gap-4 min-w-0">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-slate-800">{day.date}</span>
                      {rel && <span className="badge-info text-xs">{rel}</span>}
                    </div>
                    <span className="text-xs text-slate-400">{dayName}</span>
                  </div>

                  {/* Input status */}
                  <div className="hidden sm:block text-xs text-slate-500">
                    <span className={inputCount >= inputTotal ? 'text-success font-medium' : ''}>
                      {inputCount}/{inputTotal} files
                    </span>
                    {day.inputStatus?.lastUploaded && (
                      <span className="ml-1 text-slate-400">
                        · {format(parseISO(day.inputStatus.lastUploaded), 'MMM d HH:mm')}
                      </span>
                    )}
                  </div>

                  {/* Vendor pills */}
                  <div className="flex flex-wrap gap-1.5">
                    {(day.vendors ?? []).map(v => <VendorPill key={v.name} vendor={v} />)}
                  </div>
                </div>

                <ChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0 ml-3" />
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
