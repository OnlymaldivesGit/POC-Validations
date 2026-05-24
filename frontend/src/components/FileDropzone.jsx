import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, X, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { clsx } from 'clsx'

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function FileDropzone({ onFiles, accept, label = 'Drop files here', multiple = true }) {
  const onDrop = useCallback(accepted => {
    if (accepted.length) onFiles(accepted)
  }, [onFiles])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles, fileRejections } = useDropzone({
    onDrop,
    accept,
    multiple,
  })

  function removeFile(name) {
    const remaining = acceptedFiles.filter(f => f.name !== name)
    onFiles(remaining)
  }

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
          isDragActive
            ? 'border-brand bg-brand/5'
            : 'border-slate-300 hover:border-brand hover:bg-brand/3'
        )}
      >
        <input {...getInputProps()} />
        <UploadCloud className={clsx('w-10 h-10 mx-auto mb-3', isDragActive ? 'text-brand' : 'text-slate-400')} />
        <p className="text-sm font-medium text-slate-700">
          {isDragActive ? 'Drop to upload' : label}
        </p>
        <p className="text-xs text-slate-400 mt-1">
          {isDragActive ? '' : 'or click to browse files'}
        </p>
      </div>

      {fileRejections.length > 0 && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            {fileRejections.map(({ file, errors }) => (
              <p key={file.name}><strong>{file.name}</strong>: {errors.map(e => e.message).join(', ')}</p>
            ))}
          </div>
        </div>
      )}

      {acceptedFiles.length > 0 && (
        <ul className="space-y-1.5">
          {acceptedFiles.map(file => (
            <li key={file.name} className="flex items-center justify-between px-3 py-2 bg-white border border-slate-200 rounded-lg text-sm">
              <div className="flex items-center gap-2 min-w-0">
                <FileSpreadsheet className="w-4 h-4 text-brand flex-shrink-0" />
                <span className="font-medium text-slate-700 truncate">{file.name}</span>
                <span className="text-slate-400 text-xs flex-shrink-0">{formatBytes(file.size)}</span>
              </div>
              <button
                onClick={e => { e.stopPropagation(); removeFile(file.name) }}
                className="ml-2 text-slate-400 hover:text-danger transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
