import { BarChart3 } from 'lucide-react'

export default function Analytics() {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[60vh] gap-4 p-8">
      <BarChart3 className="w-16 h-16 text-slate-200" />
      <h2 className="text-xl font-semibold text-slate-600">Analytics — coming soon</h2>
      <p className="text-slate-400 text-sm text-center max-w-sm">
        Cross-date trends and crew utilisation over time will appear here.
      </p>
    </div>
  )
}
