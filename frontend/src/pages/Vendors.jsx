import { useState } from 'react'
import { Plus, Pencil, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { format, parseISO } from 'date-fns'
import { useVendors, useCreateVendor, useUpdateVendor, useDeleteVendor } from '../services/api'
import VendorModal from '../components/VendorModal'

export default function Vendors() {
  const [modal, setModal]   = useState({ open: false, vendor: null })
  const [delId, setDelId]   = useState(null)

  const { data, isLoading } = useVendors()
  const vendors             = data?.vendors ?? []
  const createMut = useCreateVendor()
  const updateMut = useUpdateVendor()
  const deleteMut = useDeleteVendor()

  async function handleSave(form) {
    if (modal.vendor) {
      await updateMut.mutateAsync({ id: modal.vendor.id, ...form })
    } else {
      await createMut.mutateAsync(form)
    }
    setModal({ open: false, vendor: null })
  }

  async function handleDelete(id) {
    await deleteMut.mutateAsync(id)
    setDelId(null)
  }

  const isBusy = createMut.isPending || updateMut.isPending

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Vendors</h1>
        <button onClick={() => setModal({ open: true, vendor: null })} className="btn-primary">
          <Plus className="w-4 h-4" /> Add Vendor
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">
          {[0,1,2].map(i => <div key={i} className="skeleton h-52" />)}
        </div>
      ) : vendors.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4">
          <p className="text-slate-400">No vendors yet</p>
          <button onClick={() => setModal({ open: true, vendor: null })} className="btn-primary">
            <Plus className="w-4 h-4" /> Add Vendor
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {vendors.map(v => (
            <div key={v.id} className="glass-card p-5 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-800">{v.name}</h3>
                  {v.created_at && (
                    <p className="text-xs text-slate-400 mt-0.5">
                      Created {format(parseISO(v.created_at), 'MMM d, yyyy')}
                    </p>
                  )}
                </div>
                <button onClick={() => updateMut.mutateAsync({ id: v.id, active: !v.active })}
                  className="text-slate-400 hover:text-brand transition-colors">
                  {v.active
                    ? <ToggleRight className="w-6 h-6 text-brand" />
                    : <ToggleLeft className="w-6 h-6" />}
                </button>
              </div>
              <span className={v.active ? 'badge-pass' : 'badge-warn'}>
                {v.active ? 'Active' : 'Inactive'}
              </span>
              <div className="flex gap-2 pt-2 border-t border-slate-100">
                <button onClick={() => setModal({ open: true, vendor: v })} className="btn-ghost text-xs py-1">
                  <Pencil className="w-3.5 h-3.5" /> Edit
                </button>
                <button onClick={() => setDelId(v.id)} className="btn-ghost text-xs py-1 text-danger hover:bg-red-50">
                  <Trash2 className="w-3.5 h-3.5" /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <VendorModal
        isOpen={modal.open}
        onClose={() => setModal({ open: false, vendor: null })}
        vendor={modal.vendor}
        onSave={handleSave}
        isBusy={isBusy}
      />

      {/* Delete confirm */}
      {delId && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-2xl space-y-4">
            <h2 className="font-semibold text-slate-800">Delete vendor?</h2>
            <p className="text-sm text-slate-500">This cannot be undone.</p>
            <div className="flex gap-3">
              <button onClick={() => setDelId(null)} className="btn-ghost flex-1 justify-center">Cancel</button>
              <button onClick={() => handleDelete(delId)} className="btn-primary flex-1 justify-center bg-danger hover:bg-red-600 shadow-none">
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
