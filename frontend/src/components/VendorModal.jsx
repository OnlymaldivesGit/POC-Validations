import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

const DEFAULT_COLS = {
  date:             'Date',
  flight_no:        'Flight No.',
  aircraft_no:      'Aircraft No.',
  std:              'STD -  Scheduled Departure',
  sta:              'STA -  Scheduled Arrival',
  dep_airport:      'Dep. Airport',
  arr_airport:      'Arr. Airport',
  captain:          'Captain',
  first_officer:    'First Officer',
  flight_attendant: 'Flight Attendant',
}

const COL_LABELS = {
  date:             'Date',
  flight_no:        'Flight No.',
  aircraft_no:      'Aircraft No.',
  std:              'STD (Scheduled Departure)',
  sta:              'STA (Scheduled Arrival)',
  dep_airport:      'Dep. Airport',
  arr_airport:      'Arr. Airport',
  captain:          'Captain',
  first_officer:    'First Officer',
  flight_attendant: 'Flight Attendant',
}

function emptyForm() {
  return { name: '', active: true, solver_output_columns: { ...DEFAULT_COLS } }
}

export default function VendorModal({ isOpen, onClose, vendor, onSave, isBusy }) {
  const [form, setForm] = useState(emptyForm())

  useEffect(() => {
    if (vendor) {
      setForm({
        name: vendor.name,
        active: vendor.active,
        solver_output_columns: { ...DEFAULT_COLS, ...vendor.solver_output_columns },
      })
    } else {
      setForm(emptyForm())
    }
  }, [vendor, isOpen])

  function setCol(key, val) {
    setForm(f => ({ ...f, solver_output_columns: { ...f.solver_output_columns, [key]: val } }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 flex-shrink-0">
          <h2 className="font-semibold text-slate-800">{vendor ? 'Edit Vendor' : 'Add Vendor Output'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Vendor Name</label>
            <input
              type="text"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="e.g. JEPPESEN"
              className="input-field"
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-slate-700">
            <input type="checkbox" checked={form.active}
              onChange={e => setForm(f => ({ ...f, active: e.target.checked }))}
              className="accent-brand" />
            Active
          </label>

          <div>
            <p className="text-sm font-semibold text-slate-700 mb-3">Column Mapping</p>
            <p className="text-xs text-slate-400 mb-3">Map each required field to the actual column header in this vendor's output file.</p>
            <div className="space-y-2">
              {Object.entries(COL_LABELS).map(([key, label]) => (
                <div key={key} className="grid grid-cols-2 gap-3 items-center">
                  <label className="text-xs font-medium text-slate-600">{label}</label>
                  <input
                    type="text"
                    value={form.solver_output_columns[key] ?? ''}
                    onChange={e => setCol(key, e.target.value)}
                    className="input-field text-xs"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-3 px-6 py-4 border-t border-slate-200 flex-shrink-0">
          <button onClick={onClose} className="btn-ghost flex-1 justify-center">Cancel</button>
          <button
            onClick={() => onSave(form)}
            disabled={!form.name.trim() || isBusy}
            className="btn-primary flex-1 justify-center"
          >
            {isBusy ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
