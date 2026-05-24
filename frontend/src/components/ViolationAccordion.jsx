import { useState, useRef, useEffect } from 'react'
import { ChevronDown, CheckCircle } from 'lucide-react'
import { cn } from '../lib/utils'

export default function ViolationAccordion({ category, ruleId, count, children, defaultOpen, id }) {
  const [open, setOpen] = useState(defaultOpen ?? (count > 0))
  const contentRef = useRef(null)
  const [height, setHeight] = useState(open ? 'auto' : '0')

  useEffect(() => {
    if (!contentRef.current) return
    if (open) {
      const h = contentRef.current.scrollHeight
      setHeight(`${h}px`)
      const t = setTimeout(() => setHeight('auto'), 250)
      return () => clearTimeout(t)
    } else {
      setHeight(`${contentRef.current.scrollHeight}px`)
      requestAnimationFrame(() => setHeight('0'))
    }
  }, [open])

  const isClean = count === 0

  return (
    <div
      id={id}
      style={{ scrollMarginTop: '120px' }}
      className={cn(
        'rounded-xl border overflow-hidden transition-colors',
        isClean ? 'border-green-200 bg-green-50/40' : 'border-red-200 bg-red-50/20'
      )}
    >
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-3">
          {isClean
            ? <CheckCircle className="w-4 h-4 text-success flex-shrink-0" />
            : <span className="w-4 h-4 rounded-full bg-danger/10 border border-danger/30 flex-shrink-0" />
          }
          <span className="font-semibold text-sm text-slate-800">{category}</span>
          {ruleId && <span className="badge-info text-xs">{ruleId}</span>}
          {isClean
            ? <span className="badge-pass">All clear</span>
            : <span className="badge-fail">{count} violation{count !== 1 ? 's' : ''}</span>
          }
        </div>
        <ChevronDown className={cn('w-4 h-4 text-slate-400 transition-transform', open && 'rotate-180')} />
      </button>

      <div
        ref={contentRef}
        style={{ height, overflow: 'hidden', transition: 'height 0.25s ease' }}
      >
        <div className="px-4 pb-4">{children}</div>
      </div>
    </div>
  )
}
