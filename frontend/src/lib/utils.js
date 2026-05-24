import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

export function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')
}

export const FILE_IDENTIFIERS = {
  aircrafts:                    'aircraft',
  crew_aircraft_type_matrix:    'crew_aircraft',
  crew_pairing:                 'seniority',
  log_sheet:                    'logsheet',
  crew_resource:                'crew_master',
  crew_license_expiry:          'expiry_data',
  training_pairings:            'flight_training',
  monthly_plan:                 'month_plan',
  crewstats:                    'crew_stats',
  flight_plan:                  'input_flight_plan',
}

export const FILE_TYPE_LABELS = {
  aircraft:          'Aircraft Registry',
  crew_aircraft:     'AC Qualifications',
  seniority:         'Seniority Data',
  logsheet:          'Previous Day Log',
  crew_master:       'Crew Master',
  expiry_data:       'Training Expiry',
  flight_training:   'Training Schedule',
  month_plan:        'Month Plan',
  crew_stats:        'Crew Statistics',
  input_flight_plan: 'Input Flight Plan',
}

export const REQUIRED_FILE_TYPES = Object.values(FILE_IDENTIFIERS)

export function identifyFile(filename) {
  const lower = filename.toLowerCase()
  for (const [kw, type] of Object.entries(FILE_IDENTIFIERS)) {
    if (lower.includes(kw.toLowerCase())) return type
  }
  return null
}

export function toCsv(data) {
  if (!data?.length) return ''
  const headers = Object.keys(data[0])
  const rows = data.map(r => headers.map(h => JSON.stringify(r[h] ?? '')).join(','))
  return [headers.join(','), ...rows].join('\n')
}

export function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a   = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}
