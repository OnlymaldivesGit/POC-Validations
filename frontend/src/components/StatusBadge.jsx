const MAP = {
  pass:     { cls: 'badge-pass', label: 'Pass' },
  complete: { cls: 'badge-pass', label: 'Complete' },
  clean:    { cls: 'badge-pass', label: 'Clean' },
  fail:     { cls: 'badge-fail', label: 'Fail' },
  failed:   { cls: 'badge-fail', label: 'Failed' },
  warn:     { cls: 'badge-warn', label: 'Warning' },
  pending:  { cls: 'badge-warn', label: 'Pending' },
  info:     { cls: 'badge-info', label: 'Info' },
}

export default function StatusBadge({ status, label }) {
  const s = MAP[status] || { cls: 'badge-gray', label: status || 'Unknown' }
  return <span className={s.cls}>{label || s.label}</span>
}
