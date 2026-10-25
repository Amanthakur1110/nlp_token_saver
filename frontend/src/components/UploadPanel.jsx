import { useState, useRef } from 'react'
import { uploadFile } from '../api'

/**
 * UploadPanel – file input + upload button + document info after upload.
 * Props:
 *   onUploaded(docInfo) – called when upload succeeds
 */
export default function UploadPanel({ onUploaded }) {
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [error, setError]   = useState('')
  const [docInfo, setDocInfo] = useState(null)
  const fileRef = useRef(null)

  async function handleUpload() {
    const file = fileRef.current?.files?.[0]
    if (!file) { setError('Please choose a file first.'); return }

    setStatus('loading')
    setError('')
    try {
      const info = await uploadFile(file)
      setDocInfo(info)
      setStatus('done')
      onUploaded(info)
    } catch (e) {
      setError(e.message)
      setStatus('error')
    }
  }

  return (
    <div className="border border-gray-300 p-4 mb-4 bg-white">
      <h2 className="font-bold text-lg mb-3">1. Upload Document</h2>

      <div className="flex gap-2 items-center mb-3">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="border border-gray-300 p-1 text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={status === 'loading'}
          className="border border-gray-400 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
        >
          {status === 'loading' ? 'Uploading…' : 'Upload'}
        </button>
      </div>

      <p className="text-xs text-gray-500 mb-2">Accepted: PDF, DOCX, TXT, MD – max 20 MB</p>

      {error && (
        <div className="border border-red-400 bg-red-50 text-red-700 p-2 text-sm">{error}</div>
      )}

      {docInfo && (
        <div className="border border-gray-200 bg-gray-50 p-3 text-sm mt-2">
          <p><strong>File:</strong> {docInfo.filename}</p>
          <p><strong>Characters:</strong> {docInfo.char_count.toLocaleString()}</p>
          <p><strong>Tokens (cl100k_base):</strong> {docInfo.token_count.toLocaleString()}</p>
          <p className="mt-2 text-gray-600 text-xs">Preview: {docInfo.preview}</p>
        </div>
      )}
    </div>
  )
}

