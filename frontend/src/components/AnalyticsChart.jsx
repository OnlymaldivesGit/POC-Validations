import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts'

export default function AnalyticsChart({ data = [], title, color = '#6366F1', unit = '' }) {
  const sorted = [...data].sort((a, b) => b.value - a.value).slice(0, 20)
  const extra  = data.length > 20 ? data.length - 20 : 0
  const height = Math.max(200, sorted.length * 28 + 60)

  if (!sorted.length) return (
    <div className="text-xs text-slate-400 py-4 text-center">No data</div>
  )

  return (
    <div className="glass-card p-4">
      {title && <h4 className="text-sm font-semibold text-slate-700 mb-3">{title}</h4>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={sorted} layout="vertical" margin={{ left: 0, right: 60, top: 4, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
          <XAxis type="number" tick={{ fontSize: 10 }} />
          <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 10 }} />
          <Tooltip
            formatter={v => [`${v}${unit}`, 'Value']}
            contentStyle={{ fontSize: 11, borderRadius: 8, border: '1px solid #e2e8f0' }}
          />
          <Bar dataKey="value" fill={color} radius={[0, 4, 4, 0]} maxBarSize={20}>
            <LabelList dataKey="value" position="right" style={{ fontSize: 10, fill: '#64748b' }}
              formatter={v => `${v}${unit}`} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {extra > 0 && (
        <p className="text-xs text-slate-400 mt-2 text-center">and {extra} more…</p>
      )}
    </div>
  )
}
