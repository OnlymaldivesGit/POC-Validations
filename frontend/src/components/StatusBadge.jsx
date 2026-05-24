const statusMap = {
  pass:     { cls: 'badge-pass', label: 'Pass' },
  complete: { cls: 'badge-pass', label: 'Complete' },
  fail:     { cls: 'badge-fail', label: 'Fail' },
  failed:   { cls: 'badge-fail', label: 'Failed' },
  warn:     { cls: 'badge-warn', label: 'Warning' },
  info:     { cls: 'badge-info', label: 'Info' },
}

export default function StatusBadge({ status, label }) {
  const s = statusMap[status] || statusMap.info
  return <span className={s.cls}>{label || s.label}</span>
}
