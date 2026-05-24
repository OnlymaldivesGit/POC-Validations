import { useParams, useNavigate } from 'react-router-dom'
import { format, parseISO } from 'date-fns'
import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useVendors, useFiles, useRunHistory } from '../services/api'
import { useCreateVendor } from '../services/api'
import VendorModal from '../components/VendorModal'
import InputDataTab from './InputDataTab'
import VendorTab from './VendorTab'
import CompareTab from './CompareTab'
import { REQUIRED_FILE_TYPES } from '../lib/utils'

function dayLabel(dateStr) {
  try { return format(parseISO(dateStr), 'EEEE, MMMM d yyyy') }
  catch { return dateStr }
}

export default function DayWorkspace() {
  const { date, tab = 'input' } = useParams()
  const navigate = useNavigate()

  const [vendorModal, setVendorModal] = useState(false)
  const createMut = useCreateVendor()

  const { data: vendorData } = useVendors()
  const vendors = vendorData?.vendors ?? []

  const { data: fileData }  = useFiles(date)
  const { data: runsData }  = useRunHistory({ date_from: date, date_to: date, per_page: 100 })

  const presentFiles = fileData?.inputs ?? []
  const uploadedCount = REQUIRED_FILE_TYPES.filter(t =>
    presentFiles.some(f => f.fileType === t || f.file_type === t)
  ).length

  const runs = runsData?.runs ?? []

  // Status badge logic
  function dayStatus() {
    const allRunViolations = runs.reduce((s, r) => s + (r.total_violations ?? 0), 0)
    if (runs.length === 0 && uploadedCount < REQUIRED_FILE_TYPES.length)
      return { label: 'Input incomplete', cls: 'badge-warn' }
    if (runs.length === 0)
      return { label: 'No vendor runs', cls: 'badge-gray' }
    if (allRunViolations > 0)
      return { label: `${allRunViolations} total violations`, cls: 'badge-fail' }
    return { label: 'All clean', cls: 'badge-pass' }
  }
  const status = dayStatus()

  // Active vendor from tab param
  const activeVendor = vendors.find(
    v => v.id === tab || v.name?.toLowerCase().replace(/\s+/g, '-') === tab
  )

  function tabTo(t) { navigate(`/days/${date}/${t}`) }

  function vendorTabId(v) {
    return v.name?.toLowerCase().replace(/\s+/g, '-') || v.id
  }

  function vendorBadge(v) {
    const vRuns = runs.filter(r => r.vendor?.toLowerCase() === v.name?.toLowerCase())
    if (!vRuns.length) return null
    const latest = vRuns.sort((a,b) => b.timestamp?.localeCompare(a.timestamp ?? '') ?? 0)[0]
    const count  = latest?.total_violations ?? 0
    if (count > 0) return (
      <span className="ml-1.5 inline-flex items-center justify-center w-5 h-5 rounded-full bg-danger text-white text-[10px] font-bold">
        {count > 99 ? '99+' : count}
      </span>
    )
    return <span className="ml-1.5 text-success text-xs">✓</span>
  }

  async function handleAddVendor(form) {
    const v = await createMut.mutateAsync(form)
    setVendorModal(false)
    // Navigate to the new vendor tab
    if (v?.id) tabTo(v.id)
  }

  const isInputTab   = tab === 'input'
  const isCompareTab = tab === 'compare'
  const isVendorTab  = !isInputTab && !isCompareTab

  return (
    <div className="flex flex-col h-full">
      {/* Sticky header */}
      <div className="sticky top-0 z-30 bg-white border-b border-slate-200">
        <div className="flex items-center justify-between px-6 py-3">
          <h2 className="text-lg font-bold text-slate-800">{dayLabel(date)}</h2>
          <span className={status.cls}>{status.label}</span>
        </div>

        {/* Tab bar */}
        <div className="flex items-end border-t border-slate-100 px-4 overflow-x-auto">
          {/* Input tab */}
          <button
            onClick={() => tabTo('input')}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
              isInputTab
                ? 'border-brand text-brand'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            Input Data
            <span className={`ml-1.5 badge-${uploadedCount === REQUIRED_FILE_TYPES.length ? 'pass' : 'warn'} text-xs`}>
              {uploadedCount}/{REQUIRED_FILE_TYPES.length}
            </span>
          </button>

          {/* Vendor tabs */}
          {vendors.map(v => {
            const vid    = vendorTabId(v)
            const active = tab === vid || tab === v.id
            return (
              <button
                key={v.id}
                onClick={() => tabTo(vid)}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                  active
                    ? 'border-brand text-brand'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                {v.name}{vendorBadge(v)}
              </button>
            )
          })}

          {/* Compare tab */}
          {vendors.length >= 2 && (
            <button
              onClick={() => tabTo('compare')}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                isCompareTab
                  ? 'border-brand text-brand'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Compare
            </button>
          )}

          {/* Add vendor */}
          <button
            onClick={() => setVendorModal(true)}
            className="px-3 py-2.5 text-sm text-slate-400 hover:text-brand border-b-2 border-transparent whitespace-nowrap flex items-center gap-1 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> Add
          </button>
        </div>
      </div>

      {/* Tab content — scrollable */}
      <div className="flex-1 overflow-y-auto p-6">
        {isInputTab && <InputDataTab date={date} />}
        {isVendorTab && activeVendor && <VendorTab date={date} vendor={activeVendor} key={activeVendor.id} />}
        {isVendorTab && !activeVendor && (
          <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
            <p>Vendor not found. Select a tab above.</p>
          </div>
        )}
        {isCompareTab && <CompareTab date={date} />}
      </div>

      <VendorModal
        isOpen={vendorModal}
        onClose={() => setVendorModal(false)}
        vendor={null}
        onSave={handleAddVendor}
        isBusy={createMut.isPending}
      />
    </div>
  )
}
