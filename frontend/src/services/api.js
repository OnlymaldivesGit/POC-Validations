import axios from 'axios'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// ---------------------------------------------------------------------------
// Queries
// ---------------------------------------------------------------------------

export function useRunHistory(filters = {}) {
  return useQuery({
    queryKey: ['reports', filters],
    queryFn: async () => {
      const params = {}
      if (filters.date_from) params.date_from = filters.date_from
      if (filters.date_to)   params.date_to   = filters.date_to
      if (filters.vendor)    params.vendor     = filters.vendor
      if (filters.status)    params.status     = filters.status
      if (filters.page)      params.page       = filters.page
      if (filters.per_page)  params.per_page   = filters.per_page
      const { data } = await api.get('/api/reports', { params })
      return data
    },
  })
}

export function useReport(runId) {
  return useQuery({
    queryKey: ['report', runId],
    queryFn: async () => {
      const { data } = await api.get(`/api/reports/${runId}`)
      return data
    },
    enabled: !!runId,
  })
}

export function useVendors() {
  return useQuery({
    queryKey: ['vendors'],
    queryFn: async () => {
      const { data } = await api.get('/api/vendors')
      return data
    },
  })
}

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

// ---------------------------------------------------------------------------
// Mutations
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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['reports'] })
    },
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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vendors'] })
    },
  })
}

export function useUpdateVendor() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }) => {
      const { data } = await api.put(`/api/vendors/${id}`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vendors'] })
    },
  })
}

export function useDeleteVendor() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id) => {
      await api.delete(`/api/vendors/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vendors'] })
    },
  })
}

// ---------------------------------------------------------------------------
// Direct download helpers
// ---------------------------------------------------------------------------

export async function downloadExcel(runId) {
  const res = await api.get(`/api/reports/${runId}/excel`, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a   = document.createElement('a')
  a.href    = url
  a.download = `validation_report_${runId}.xlsx`
  a.click()
  URL.revokeObjectURL(url)
}

export async function downloadHtml(runId) {
  const res = await api.get(`/api/reports/${runId}/html`, { responseType: 'text' })
  return res.data
}
