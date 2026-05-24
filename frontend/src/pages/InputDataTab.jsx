import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  FileSpreadsheet, CheckCircle, XCircle, RefreshCw, Loader2, AlertCircle, UploadCloud,
} from 'lucide-react'
import { format, parseISO } from 'date-fns'
import {
  useFiles, useUploadFile, useValidateInputs,
} from '../services/api'
import ViolationAccordion from '../components/ViolationAccordion'
import ViolationTable from '../components/ViolationTable'
import {
  FILE_TYPE_LABELS, REQUIRED_FILE_TYPES, identifyFile,
} from '../lib/utils'

export default function InputDataTab({ date }) {
  const { data: fileData, isLoading: filesLoading, refetch } = useFiles(date)
  const uploadMut   = useUploadFile()
  const validateMut = useValidateInputs()

  const [uploading, setUploading]     = useState({}) // fileType → bool
  const [toastMsg,  setToastMsg]      = useState('')
  const [inputResult, setInputResult] = useState(null)

  const presentFiles = fileData?.inputs ?? []

  function filePresent(type) {
    return presentFiles.some(f => f.fileType === type || f.file_type === type)
  }
  function fileInfo(type) {
    return presentFiles.find(f => f.fileType === type || f.file_type === type)
  }

  // Full-area drop
  const onDrop = useCallback(async (accepted) => {
    const byType = {}
    const unrecognised = []
    accepted.forEach(f => {
      const type = identifyFile(f.name)
      if (type) byType[type] = f
      else unrecognised.push(f.name)
    })
    if (unrecognised.length) {
      setToastMsg(`Could not identify: ${unrecognised.join(', ')}`)
      setTimeout(() => setToastMsg(''), 4000)
    }
    for (const [fileType, file] of Object.entries(byType)) {
      setUploading(u => ({ ...u, [fileType]: true }))
      try {
        await uploadMut.mutateAsync({ date, fileType, file })
      } catch (e) {
        console.error(e)
      } finally {
        setUploading(u => ({ ...u, [fileType]: false }))
      }
    }
  }, [date, uploadMut])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls', '.xlsm'],
    },
    noClick: true,
  })

  async function handleReupload(type) {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.xlsx,.xls,.xlsm'
    input.onchange = async e => {
      const file = e.target.files[0]
      if (!file) return
      setUploading(u => ({ ...u, [type]: true }))
      try { await uploadMut.mutateAsync({ date, fileType: type, file }) }
      finally { setUploading(u => ({ ...u, [type]: false })) }
    }
    input.click()
  }

  async function handleValidate() {
    const presentFileObjs = [] // can't re-use File objects; use GitHub inputs flag
    try {
      // We use GitHub inputs path — files already on GitHub
      const form = new FormData()
      form.append('date', date)
      // Pass empty files list + tell backend to load from GitHub
      // This is handled by calling the inputs endpoint without files
      // The backend will look them up from GitHub
      // NOTE: The /api/validate/inputs endpoint requires actual files to be uploaded.
      // For input validation from already-uploaded files, we send the date only
      // and the backend will need to support GitHub loading.
      // For now we show a message.
      setInputResult({ _msg: 'Input validation requires uploading files directly. Use the /run page for full validation with GitHub inputs.' })
    } catch (e) {
      console.error(e)
    }
  }

  const uploadedCount = REQUIRED_FILE_TYPES.filter(filePresent).length

  return (
    <div
      {...getRootProps()}
      className={`space-y-6 relative ${isDragActive ? 'ring-4 ring-brand/30 rounded-2xl' : ''}`}
    >
      <input {...getInputProps()} />

      {isDragActive && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-brand/10 border-4 border-dashed border-brand rounded-2xl pointer-events-none">
          <UploadCloud className="w-12 h-12 text-brand mb-3" />
          <p className="text-brand font-semibold text-lg">Drop files anywhere to upload</p>
        </div>
      )}

      {toastMsg && (
        <div className="flex items-center gap-2 px-4 py-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {toastMsg}
        </div>
      )}

      {/* Panel 1 — File Manager */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-800">Input Files</h3>
            <span className={`badge-${uploadedCount === REQUIRED_FILE_TYPES.length ? 'pass' : 'warn'}`}>
              {uploadedCount}/{REQUIRED_FILE_TYPES.length}
            </span>
          </div>
          {presentFiles.length > 0 && (
            <span className="text-xs text-slate-400">
              Drop files anywhere to upload
            </span>
          )}
        </div>

        {filesLoading ? (
          <div className="grid grid-cols-2 gap-2">
            {[...Array(10)].map((_, i) => <div key={i} className="skeleton h-16" />)}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {REQUIRED_FILE_TYPES.map(type => {
              const present = filePresent(type)
              const info    = fileInfo(type)
              const busy    = uploading[type]
              return (
                <div key={type} className={`flex items-center justify-between px-3 py-2.5 rounded-lg border text-sm ${
                  present ? 'bg-green-50/60 border-green-200' : 'bg-red-50/40 border-red-200'
                }`}>
                  <div className="flex items-center gap-2 min-w-0">
                    {busy ? (
                      <Loader2 className="w-4 h-4 text-brand animate-spin flex-shrink-0" />
                    ) : present ? (
                      <CheckCircle className="w-4 h-4 text-success flex-shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-danger flex-shrink-0" />
                    )}
                    <div className="min-w-0">
                      <p className="font-medium text-xs text-slate-700 truncate">{FILE_TYPE_LABELS[type]}</p>
                      {present && info ? (
                        <p className="text-xs text-slate-400 truncate">
                          {info.filename && info.filename.length > 24 ? info.filename.slice(0, 22) + '…' : info.filename}
                        </p>
                      ) : (
                        <p className="text-xs text-slate-400">Not uploaded</p>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => handleReupload(type)}
                    title="Re-upload"
                    className="ml-2 text-slate-400 hover:text-brand transition-colors flex-shrink-0"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                </div>
              )
            })}
          </div>
        )}

        {/* Drop hint when no files */}
        {!filesLoading && uploadedCount === 0 && (
          <div className="mt-4 border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
            <UploadCloud className="w-8 h-8 mx-auto text-slate-300 mb-2" />
            <p className="text-sm text-slate-500">Drop all 10 input files here to auto-upload</p>
            <p className="text-xs text-slate-400 mt-1">Files are identified by filename keyword matching</p>
          </div>
        )}
      </div>

      {/* Panel 2 — Input Health */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-slate-800">Input Health</h3>
        </div>

        {!inputResult ? (
          <div className="flex flex-col items-center justify-center py-10 gap-4 text-center">
            <FileSpreadsheet className="w-10 h-10 text-slate-300" />
            <p className="text-sm text-slate-400">Validate your input files to check for data issues</p>
            <button onClick={handleValidate} disabled={uploadedCount < REQUIRED_FILE_TYPES.length}
              className="btn-primary">
              <CheckCircle className="w-4 h-4" /> Validate Inputs
            </button>
            {uploadedCount < REQUIRED_FILE_TYPES.length && (
              <p className="text-xs text-slate-400">Upload all {REQUIRED_FILE_TYPES.length} files first</p>
            )}
          </div>
        ) : inputResult._msg ? (
          <div className="flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            {inputResult._msg}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className={`flex-1 text-center p-3 rounded-lg ${(inputResult.validation_1?.length ?? 0) > 0 ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
                <p className={`text-2xl font-bold ${(inputResult.validation_1?.length ?? 0) > 0 ? 'text-danger' : 'text-success'}`}>
                  {inputResult.validation_1?.length ?? 0}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">crew missing data</p>
              </div>
              <div className={`flex-1 text-center p-3 rounded-lg ${(inputResult.validation_2?.length ?? 0) > 0 ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
                <p className={`text-2xl font-bold ${(inputResult.validation_2?.length ?? 0) > 0 ? 'text-danger' : 'text-success'}`}>
                  {inputResult.validation_2?.length ?? 0}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">crew missing stats</p>
              </div>
            </div>
            <ViolationAccordion category="Missing Resource Data" ruleId="I-1" count={inputResult.validation_1?.length ?? 0} id="i1">
              <ViolationTable data={inputResult.validation_1 ?? []} emptyMessage="All resource data complete" />
            </ViolationAccordion>
            <ViolationAccordion category="Missing Statistics" ruleId="I-2" count={inputResult.validation_2?.length ?? 0} id="i2">
              <ViolationTable data={inputResult.validation_2 ?? []} emptyMessage="All statistics populated" />
            </ViolationAccordion>
          </div>
        )}
      </div>
    </div>
  )
}
