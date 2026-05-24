import axios from 'axios'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toCsv, triggerDownload } from '../lib/utils'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// ---------------------------------------------------------------------------
// Days — derived from run index (no native /api/days endpoint yet)
// ---------------------------------------------------------------------------

export function useDays() {
  return useQuery({
    queryKey: ['days'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/days')
        return data
      } catch {
        // Fallback: derive from run index
        const { data: rd } = await api.get('/api/reports', { params: { per_page: 500 } })
        const runs = rd.runs ?? []
        const byDate = {}
        runs.forEach(r => {
          if (!byDate[r.date]) {
            byDate[r.date] = { date: r.date, inputStatus: { count: 0, total: 10, lastUploaded: null }, vendors: [] }
          }
          const vlist = byDate[r.date].vendors
          const existing = vlist.find(v => v.name === r.vendor)
          if (!existing) {
            vlist.push({ name: r.vendor, status: r.total_violations > 0 ? 'violations' : 'clean', violationCount: r.total_violations, lastRun: r.timestamp })
          } else if (r.timestamp > existing.lastRun) {
            existing.status = r.total_violations > 0 ? 'violations' : 'clean'
            existing.violationCount = r.total_violations
            existing.lastRun = r.timestamp
          }
        })
        return Object.values(byDate).sort((a, b) => b.date.localeCompare(a.date))
      }
    },
  })
}

// ---------------------------------------------------------------------------
// Files
// ---------------------------------------------------------------------------

export function useFiles(date) {
  return useQuery({
    queryKey: ['files', date],
    queryFn: async () => {
      const { data } = await api.get(`/api/files/${date}`)
      return data
    },
    enabled: !!date,
  })
}

export function useUploadFile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ date, fileType, file }) => {
      const form = new FormData()
      form.append('date', date)
      form.append('file_type', fileType)
      form.append('file', file)
      const { data } = await api.post('/api/files/upload', form)
      return data
    },
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: ['files', date] })
      qc.invalidateQueries({ queryKey: ['days'] })
    },
  })
}

// ---------------------------------------------------------------------------
// Input validation
// ---------------------------------------------------------------------------

export function useValidateInputs() {
  return useMutation({
    mutationFn: async ({ date, files }) => {
      const form = new FormData()
      form.append('date', date)
      files.forEach(f => form.append('files', f))
      const { data } = await api.post('/api/validate/inputs', form)
      return data
    },
  })
}

// General run history listing
export function useRunHistory(filters = {}) {
  return useQuery({
    queryKey: ['reports', filters],
    queryFn: async () => {
      const params = {}
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to)   params.date_to   = filters.date_to
      if (filters.vendor)    params.vendor     = filters.vendor
      if (filters.status)    params.status     = filters.status
      params.page     = filters.page     || 1
      params.per_page = filters.per_page || 20
      const { data } = await api.get('/api/reports', { params })
      return data
    },
  })
}

// ---------------------------------------------------------------------------
// Full constraints validation
// ---------------------------------------------------------------------------

export function useRunValidation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ date, vendorId, files, useGithubInputs = false }) => {
      const form = new FormData()
      form.append('date', date)
      form.append('vendor_id', vendorId)
      form.append('use_github_inputs', useGithubInputs)
      files.forEach(f => form.append('files', f))
      const { data } = await api.post('/api/validate', form)
      return data
    },
    onSuccess: (_, { date }) => {
      qc.invalidateQueries({ queryKey: ['reports'] })
      qc.invalidateQueries({ queryKey: ['days'] })
      qc.invalidateQueries({ queryKey: ['vendorRuns'] })
    },
  })
}

export function useVendorRuns(date, vendorName) {
  return useQuery({
    queryKey: ['vendorRuns', date, vendorName],
    queryFn: async () => {
      const { data } = await api.get('/api/reports', {
        params: { date_from: date, date_to: date, vendor: vendorName, per_page: 50 },
      })
      return data.runs ?? []
    },
    enabled: !!date && !!vendorName,
  })
}

export function useRunDetail(runId) {
  return useQuery({
    queryKey: ['runDetail', runId],
    queryFn: async () => {
      const { data } = await api.get(`/api/reports/${runId}`)
      return data
    },
    enabled: !!runId,
  })
}

// ---------------------------------------------------------------------------
// Vendors
// ---------------------------------------------------------------------------

export function useVendors() {
  return useQuery({
    queryKey: ['vendors'],
    queryFn: async () => {
      const { data } = await api.get('/api/vendors')
      return Array.isArray(data) ? { vendors: data } : data
    },
  })
}

export function useCreateVendor() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await api.post('/api/vendors', payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }),
  })
}

export function useUpdateVendor() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }) => {
      const { data } = await api.put(`/api/vendors/${id}`, payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }),
  })
}

export function useDeleteVendor() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id) => { await api.delete(`/api/vendors/${id}`) },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vendors'] }),
  })
}

// ---------------------------------------------------------------------------
// Downloads
// ---------------------------------------------------------------------------

export async function downloadExcel(runId) {
  const res = await api.get(`/api/reports/${runId}/excel`, { responseType: 'blob' })
  triggerDownload(res.data, `validation_report_${runId}.xlsx`)
}

export async function downloadHtml(runId) {
  const res = await api.get(`/api/reports/${runId}/html`, { responseType: 'text' })
  return res.data
}

export function downloadCompareCSV(date, data) {
  const blob = new Blob([toCsv(data)], { type: 'text/csv' })
  triggerDownload(blob, `compare_${date}.csv`)
}
