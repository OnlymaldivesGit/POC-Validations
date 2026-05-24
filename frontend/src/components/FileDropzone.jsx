import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, X, FileSpreadsheet, AlertCircle } from 'lucide-react'
import { cn, formatBytes } from '../lib/utils'

export default function FileDropzone({ onFiles, accept, label = 'Drop files here', multiple = true, className = '' }) {
  const onDrop = useCallback(accepted => { if (accepted.length) onFiles(accepted) }, [onFiles])

  const { getRootProps, getInputProps, isDragActive, acceptedFiles, fileRejections, isDragAccept } =
    useDropzone({ onDrop, accept, multiple })

  function remove(name) { onFiles(acceptedFiles.filter(f => f.name !== name)) }

  return (
    <div className={cn('space-y-3', className)}>
      <div {...getRootProps()} className={cn(
        'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
        isDragActive ? 'border-brand bg-brand/5 border-solid' : 'border-slate-300 hover:border-brand hover:bg-slate-50'
      )}>
        <input {...getInputProps()} />
        <UploadCloud className={cn('w-10 h-10 mx-auto mb-3', isDragActive ? 'text-brand' : 'text-slate-300')} />
        <p className="text-sm font-medium text-slate-600">
          {isDragActive ? 'Drop to upload' : label}
        </p>
        {!isDragActive && <p className="text-xs text-slate-400 mt-1">or click to browse</p>}
      </div>

      {fileRejections.length > 0 && (
        <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>{fileRejections.map(({ file, errors }) => (
            <p key={file.name}><strong>{file.name}</strong>: {errors.map(e => e.message).join(', ')}</p>
          ))}</div>
        </div>
      )}

      {acceptedFiles.length > 0 && (
        <ul className="space-y-1.5">
          {acceptedFiles.map(f => (
            <li key={f.name} className="flex items-center justify-between px-3 py-2 bg-white border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2 min-w-0">
                <FileSpreadsheet className="w-4 h-4 text-brand flex-shrink-0" />
                <span className="text-sm font-medium text-slate-700 truncate">{f.name}</span>
                <span className="text-xs text-slate-400 flex-shrink-0">{formatBytes(f.size)}</span>
              </div>
              <button onClick={e => { e.stopPropagation(); remove(f.name) }} className="ml-2 text-slate-400 hover:text-danger">
                <X className="w-4 h-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
