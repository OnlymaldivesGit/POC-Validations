import { useState } from 'react'
import { CheckCircle, Circle, Loader2, AlertCircle } from 'lucide-react'
import {
  useVendors, useFiles, useValidateInputs, useRunValidation, downloadExcel, downloadHtml,
} from '../services/api'
import ProgressStepper from '../components/ProgressStepper'
import FileDropzone from '../components/FileDropzone'
import ViolationTable from '../components/ViolationTable'
import ViolationSummaryGrid from '../components/ViolationSummaryGrid'

const STEPS = ['Setup', 'Input Files', 'Solver Output', 'Results']

const FILE_IDENTIFIERS = {
  aircrafts:                   'aircraft',
  crew_aircraft_type_matrix:   'crew_aircraft',
  crew_pairing:                'seniority',
  log_sheet:                   'logsheet',
  crew_resource:               'crew_master',
  crew_license_expiry:         'expiry_data',
  training_pairings:           'flight_training',
  monthly_plan:                'month_plan',
  crewstats:                   'crew_stats',
  flight_plan:                 'input_flight_plan',
}

function identifyFile(filename) {
  const lower = filename.toLowerCase()
  for (const [kw, type] of Object.entries(FILE_IDENTIFIERS)) {
    if (lower.includes(kw)) return type
  }
  return null
}

export default function RunValidator() {
  const [step, setStep]           = useState(0)
  const [completedSteps, setCompleted] = useState([])
  const [date, setDate]           = useState('')
  const [vendorId, setVendorId]   = useState('')
  const [inputFiles, setInputFiles]     = useState([])
  const [solverFile, setSolverFile]     = useState(null)
  const [inputResult, setInputResult]   = useState(null)
  const [validationResult, setValidResult] = useState(null)
  const [activeTab, setActiveTab] = useState(0)
  const [viewHtml, setViewHtml]   = useState(null)

  const { data: vendorData } = useVendors()
  const vendors = vendorData?.vendors ?? []

  const { data: fileData, isLoading: filesLoading } = useFiles(date)

  const validateInputsMut  = useValidateInputs()
  const runValidationMut   = useRunValidation()

  function complete(idx) {
    setCompleted(prev => prev.includes(idx) ? prev : [...prev, idx])
  }

  const fileRows = inputFiles.map(f => ({
    file: f,
    type: identifyFile(f.name) || 'unrecognised',
  }))

  async function handleValidateInputs() {
    try {
      const result = await validateInputsMut.mutateAsync({ date, files: inputFiles })
      setInputResult(result)
      complete(1)
    } catch (e) {
      console.error(e)
    }
  }

  async function handleRunValidation() {
    if (!solverFile) return
    try {
      const allFiles = [...inputFiles, solverFile]
      const result = await runValidationMut.mutateAsync({ date, vendorId, files: allFiles })
      setValidResult(result)
      complete(2)
      setStep(3)
    } catch (e) {
      console.error(e)
    }
  }

  function reset() {
    setStep(0)
    setCompleted([])
    setDate('')
    setVendorId('')
    setInputFiles([])
    setSolverFile(null)
    setInputResult(null)
    setValidResult(null)
  }

  const githubFiles = fileData?.inputs ?? {}

  const INPUT_FILE_TYPES = Object.values(FILE_IDENTIFIERS)
  const expectedFiles = INPUT_FILE_TYPES.map(type => ({
    type,
    inGithub: Object.values(githubFiles).some(p => p.includes(type)),
  }))

  const violationCategories = validationResult
    ? Object.entries(validationResult)
        .filter(([k]) => !['run_id','date','vendor','timestamp','status',
                           'total_violations','violation_counts','available_crew',
                           'scheduled_crew'].includes(k))
        .filter(([, v]) => Array.isArray(v) && v.length > 0)
    : []

  return (
    <div className="p-8 space-y-8 max-w-4xl">
      <h1 className="page-title">Run Validator</h1>

      <ProgressStepper steps={STEPS} currentStep={step} completedSteps={completedSteps} />

      {/* STEP 0 — Setup */}
      {step === 0 && (
        <div className="glass-card p-6 space-y-5">
          <h2 className="section-title">Step 1: Setup</h2>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Schedule Date</label>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              className="input-field max-w-xs"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Vendor</label>
            <select
              value={vendorId}
              onChange={e => setVendorId(e.target.value)}
              className="input-field max-w-xs"
            >
              <option value="">— Select vendor —</option>
              {vendors.map(v => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </select>
          </div>

          {date && (
            <div>
              <p className="text-sm font-medium text-slate-700 mb-2">GitHub Input Files</p>
              {filesLoading ? (
                <p className="text-sm text-slate-400">Checking GitHub…</p>
              ) : (
                <div className="grid grid-cols-2 gap-1.5 text-xs">
                  {expectedFiles.map(({ type, inGithub }) => (
                    <div key={type} className="flex items-center gap-2 text-slate-600">
                      {inGithub
                        ? <CheckCircle className="w-4 h-4 text-success flex-shrink-0" />
                        : <Circle className="w-4 h-4 text-slate-300 flex-shrink-0" />}
                      {type}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          <button
            onClick={() => { complete(0); setStep(1) }}
            disabled={!date || !vendorId}
            className="btn-primary"
          >
            Continue
          </button>
        </div>
      )}

      {/* STEP 1 — Input Files */}
      {step === 1 && (
        <div className="glass-card p-6 space-y-5">
          <h2 className="section-title">Step 2: Input Files</h2>

          <FileDropzone
            label="Drop all 10 input Excel files here"
            accept={{ 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
                      'application/vnd.ms-excel': ['.xls', '.xlsm'] }}
            multiple
            onFiles={setInputFiles}
          />

          {fileRows.length > 0 && (
            <div className="space-y-1.5">
              {fileRows.map(({ file, type }) => (
                <div key={file.name} className="flex items-center justify-between text-xs px-3 py-2 bg-slate-50 rounded-lg">
                  <span className="font-medium text-slate-700 truncate max-w-[240px]">{file.name}</span>
                  <span className={type === 'unrecognised' ? 'badge-warn' : 'badge-info'}>{type}</span>
                </div>
              ))}
            </div>
          )}

          {validateInputsMut.isError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {validateInputsMut.error?.response?.data?.detail || 'Validation failed'}
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setStep(0)} className="btn-ghost">Back</button>
            <button
              onClick={handleValidateInputs}
              disabled={inputFiles.length === 0 || validateInputsMut.isPending}
              className="btn-primary flex items-center gap-2"
            >
              {validateInputsMut.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Upload & Validate Inputs
            </button>
          </div>

          {inputResult && (
            <div className="space-y-4 pt-4 border-t border-slate-100">
              <ViolationTable
                data={inputResult.validation_1}
                title="Missing Resource Data"
                ruleId="I-1"
                emptyMessage="All resource data is complete"
              />
              <ViolationTable
                data={inputResult.validation_2}
                title="Missing Statistics"
                ruleId="I-2"
                emptyMessage="All statistics are populated"
              />
              <button onClick={() => { complete(1); setStep(2) }} className="btn-primary">
                Continue to Solver Output
              </button>
            </div>
          )}
        </div>
      )}

      {/* STEP 2 — Solver Output */}
      {step === 2 && (
        <div className="glass-card p-6 space-y-5">
          <h2 className="section-title">Step 3: Solver Output</h2>

          <FileDropzone
            label="Drop solver output Excel file"
            accept={{ 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
                      'application/vnd.ms-excel': ['.xls'] }}
            multiple={false}
            onFiles={files => setSolverFile(files[0] || null)}
          />

          {runValidationMut.isError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {runValidationMut.error?.response?.data?.detail || 'Validation failed'}
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setStep(1)} className="btn-ghost">Back</button>
            <button
              onClick={handleRunValidation}
              disabled={!solverFile || runValidationMut.isPending}
              className="btn-primary flex items-center gap-2"
            >
              {runValidationMut.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Run Full Validation
            </button>
          </div>
        </div>
      )}

      {/* STEP 3 — Results */}
      {step === 3 && validationResult && (
        <div className="space-y-6">
          <div className="glass-card p-6">
            <h2 className="section-title">Validation Results</h2>
            <div className="flex items-center gap-4 text-sm text-slate-500 mb-4">
              <span>Run ID: <strong className="text-slate-700">{validationResult.run_id}</strong></span>
              <span>Date: <strong className="text-slate-700">{validationResult.date}</strong></span>
              <span>Vendor: <strong className="text-slate-700">{validationResult.vendor}</strong></span>
            </div>
            <ViolationSummaryGrid violationCounts={validationResult.violation_counts || {}} />
          </div>

          {violationCategories.length > 0 && (
            <div className="glass-card overflow-hidden">
              <div className="flex border-b border-slate-200 overflow-x-auto">
                {violationCategories.map(([key], i) => (
                  <button
                    key={key}
                    onClick={() => setActiveTab(i)}
                    className={`px-4 py-3 text-xs font-semibold whitespace-nowrap transition-colors ${
                      activeTab === i
                        ? 'bg-brand text-white'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {key.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
              <div className="p-4">
                {violationCategories[activeTab] && (
                  <ViolationTable
                    data={violationCategories[activeTab][1]}
                    title={violationCategories[activeTab][0].replace(/_/g, ' ')}
                  />
                )}
              </div>
            </div>
          )}

          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => downloadExcel(validationResult.run_id)}
              className="btn-outline"
            >
              Download Excel
            </button>
            <button
              onClick={async () => { const html = await downloadHtml(validationResult.run_id); setViewHtml(html) }}
              className="btn-outline"
            >
              View HTML Report
            </button>
            <button onClick={reset} className="btn-ghost">Run Another</button>
          </div>
        </div>
      )}

      {/* HTML modal */}
      {viewHtml && (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <h2 className="font-semibold">HTML Report</h2>
              <button onClick={() => setViewHtml(null)} className="btn-ghost">✕ Close</button>
            </div>
            <div className="flex-1 overflow-hidden">
              <iframe srcDoc={viewHtml} title="HTML Report" className="w-full h-full border-0" sandbox="allow-scripts" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
