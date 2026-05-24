import { clsx } from 'clsx'
import { Check } from 'lucide-react'

export default function ProgressStepper({ steps, currentStep, completedSteps = [] }) {
  return (
    <div className="flex items-start gap-0">
      {steps.map((label, i) => {
        const isCompleted = completedSteps.includes(i)
        const isCurrent   = i === currentStep
        const isFuture    = !isCompleted && !isCurrent

        return (
          <div key={i} className="flex items-start flex-1 min-w-0">
            <div className="flex flex-col items-center flex-shrink-0">
              <div
                className={clsx(
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold border-2 transition-all',
                  isCompleted && 'bg-brand border-brand text-white',
                  isCurrent   && 'bg-white border-brand text-brand',
                  isFuture    && 'bg-white border-slate-300 text-slate-400'
                )}
              >
                {isCompleted ? <Check className="w-4 h-4" /> : i + 1}
              </div>
              <span
                className={clsx(
                  'text-xs font-medium mt-1.5 text-center max-w-[80px]',
                  isCurrent   ? 'text-brand' : 'text-slate-400'
                )}
              >
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div
                className={clsx(
                  'h-0.5 flex-1 mt-4 mx-1 transition-all',
                  isCompleted ? 'bg-brand' : 'bg-slate-200'
                )}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
