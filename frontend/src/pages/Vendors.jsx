import { useState } from 'react'
import { Plus, Pencil, Trash2, ToggleLeft, ToggleRight, X } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { useVendors, useCreateVendor, useUpdateVendor, useDeleteVendor } from '../services/api'

const DEFAULT_COLUMNS = {
  date:            'Date',
  flight_no:       'Flight No.',
  aircraft_no:     'Aircraft No.',
  std:             'STD -  Scheduled Departure',
  sta:             'STA -  Scheduled Arrival',
  dep_airport:     'Dep. Airport',
  arr_airport:     'Arr. Airport',
  captain:         'Captain',
  first_officer:   'First Officer',
  flight_attendant:'Flight Attendant',
}

const COLUMN_LABELS = {
  date:            'Date',
  flight_no:       'Flight No.',
  aircraft_no:     'Aircraft No.',
  std:             'STD (Scheduled Departure)',
  sta:             'STA (Scheduled Arrival)',
  dep_airport:     'Dep. Airport',
  arr_airport:     'Arr. Airport',
  captain:         'Captain',
  first_officer:   'First Officer',
  flight_attendant:'Flight Attendant',
}

function emptyForm() {
  return { name: '', active: true, solver_output_columns: { ...DEFAULT_COLUMNS } }
}

export default function Vendors() {
  const [showModal, setShowModal] = useState(false)
  const [editing, setEditing]     = useState(null)
  const [form, setForm]           = useState(emptyForm())
  const [deleteConfirm, setDeleteConfirm] = useState(null)

  const { data, isLoading }  = useVendors()
  const vendors              = data?.vendors ?? []
  const createMut            = useCreateVendor()
  const updateMut            = useUpdateVendor()
  const deleteMut            = useDeleteVendor()

  function openAdd() {
    setEditing(null)
    setForm(emptyForm())
    setShowModal(true)
  }

  function openEdit(v) {
    setEditing(v)
    setForm({
      name: v.name,
      active: v.active,
      solver_output_columns: { ...DEFAULT_COLUMNS, ...v.solver_output_columns },
    })
    setShowModal(true)
  }

  async function handleSave() {
    const payload = {
      name: form.name,
      active: form.active,
      solver_output_columns: form.solver_output_columns,
    }
    if (editing) {
      await updateMut.mutateAsync({ id: editing.id, ...payload })
    } else {
      await createMut.mutateAsync(payload)
    }
    setShowModal(false)
  }

  async function toggleActive(v) {
    await updateMut.mutateAsync({ id: v.id, active: !v.active })
  }

  async function handleDelete(id) {
    await deleteMut.mutateAsync(id)
    setDeleteConfirm(null)
  }

  function setCol(key, val) {
    setForm(f => ({
      ...f,
      solver_output_columns: { ...f.solver_output_columns, [key]: val },
    }))
  }

  const isBusy = createMut.isPending || updateMut.isPending

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="page-title">Vendors</h1>
        <button onClick={openAdd} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Vendor
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">
          {[0,1,2].map(i => <div key={i} className="animate-pulse bg-slate-200 rounded-xl h-52" />)}
        </div>
      ) : vendors.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <p className="text-lg font-medium text-slate-500">No vendors yet</p>
          <button onClick={openAdd} className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" /> Add Vendor
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {vendors.map(v => (
            <div key={v.id} className="glass-card p-5 space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-800">{v.name}</h3>
                  {v.created_at && (
                    <p className="text-xs text-slate-400 mt-0.5">
                      Created {format(parseISO(v.created_at), 'MMM d, yyyy')}
                    </p>
                  )}
                </div>
                <button onClick={() => toggleActive(v)} className="text-slate-400 hover:text-brand transition-colors">
                  {v.active
                    ? <ToggleRight className="w-6 h-6 text-brand" />
                    : <ToggleLeft className="w-6 h-6" />}
                </button>
              </div>

              <span className={v.active ? 'badge-pass' : 'badge-warn'}>
                {v.active ? 'Active' : 'Inactive'}
              </span>

              <div className="flex gap-2 pt-2 border-t border-slate-100">
                <button
                  onClick={() => openEdit(v)}
                  className="btn-ghost flex items-center gap-1.5 text-xs"
                >
                  <Pencil className="w-3.5 h-3.5" /> Edit
                </button>
                <button
                  onClick={() => setDeleteConfirm(v.id)}
                  className="btn-ghost flex items-center gap-1.5 text-xs text-danger hover:bg-red-50"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 sticky top-0 bg-white z-10">
              <h2 className="font-semibold text-slate-800">{editing ? 'Edit Vendor' : 'Add Vendor'}</h2>
              <button onClick={() => setShowModal(false)} className="btn-ghost p-1">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="px-6 py-5 space-y-5">
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

              <div>
                <label className="flex items-center gap-2 cursor-pointer text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={form.active}
                    onChange={e => setForm(f => ({ ...f, active: e.target.checked }))}
                    className="accent-brand"
                  />
                  Active
                </label>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-700 mb-3">Column Mapping</p>
                <div className="space-y-2">
                  {Object.entries(COLUMN_LABELS).map(([key, label]) => (
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

            <div className="flex gap-3 px-6 py-4 border-t border-slate-200 sticky bottom-0 bg-white">
              <button onClick={() => setShowModal(false)} className="btn-ghost flex-1">Cancel</button>
              <button
                onClick={handleSave}
                disabled={!form.name.trim() || isBusy}
                className="btn-primary flex-1"
              >
                {isBusy ? 'Saving…' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete confirm dialog */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl space-y-4">
            <h2 className="font-semibold text-slate-800">Delete Vendor?</h2>
            <p className="text-sm text-slate-500">This action cannot be undone.</p>
            <div className="flex gap-3">
              <button onClick={() => setDeleteConfirm(null)} className="btn-ghost flex-1">Cancel</button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="btn-primary flex-1 bg-danger hover:bg-red-600 shadow-none"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
