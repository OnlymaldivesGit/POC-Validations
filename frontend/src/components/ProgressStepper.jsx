import { Check } from 'lucide-react'
import { cn } from '../lib/utils'

export default function ProgressStepper({ steps, currentStep, completedSteps = [] }) {
  return (
    <div className="flex items-start">
      {steps.map((label, i) => {
        const done    = completedSteps.includes(i)
        const current = i === currentStep
        const future  = !done && !current
        return (
          <div key={i} className="flex items-start flex-1 min-w-0">
            <div className="flex flex-col items-center flex-shrink-0">
              <div className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold border-2 transition-all',
                done    && 'bg-brand border-brand text-white',
                current && 'bg-white border-brand text-brand',
                future  && 'bg-white border-slate-200 text-slate-400'
              )}>
                {done ? <Check className="w-4 h-4" /> : i + 1}
              </div>
              <span className={cn('text-xs font-medium mt-1.5 text-center max-w-[80px]', current ? 'text-brand' : 'text-slate-400')}>
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={cn('h-0.5 flex-1 mt-4 mx-1 transition-all', done ? 'bg-brand' : 'bg-slate-200')} />
            )}
          </div>
        )
      })}
    </div>
  )
}
