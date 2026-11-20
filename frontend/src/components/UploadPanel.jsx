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
    <section className="panel" aria-labelledby="upload-heading">
      <div className="panel-heading">
        <span className="step-number">01</span>
        <div>
          <h2 id="upload-heading" className="panel-title">Upload your document</h2>
          <p className="panel-subtitle">Start with a file you want to make more efficient.</p>
        </div>
      </div>

      <div className="upload-controls">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          disabled={status === 'loading'}
          className="file-input"
          aria-label="Choose a document to upload"
        />
        <button
          onClick={handleUpload}
          disabled={status === 'loading'}
          className="primary-button"
        >
          {status === 'loading' && (
            <span className="spinner" aria-hidden="true" />
          )}
          {status === 'loading' ? 'Processing…' : 'Upload document'}
        </button>
      </div>

      {status === 'loading' && (
        <p className="supporting-text" role="status" aria-live="polite">
          Your document is being uploaded and prepared. This may take a moment for large files.
        </p>
      )}

      <p className="supporting-text">PDF, DOCX, TXT, or MD · Maximum file size 20 MB</p>

      {error && (
        <div className="message message-error" role="alert">{error}</div>
      )}

      {docInfo && (
        <div className="document-info" aria-label="Uploaded document details">
          <div className="document-stat">
            <span>FILE</span>
            <strong title={docInfo.filename}>{docInfo.filename}</strong>
          </div>
          <div className="document-stat">
            <span>CHARACTERS</span>
            <strong>{docInfo.char_count.toLocaleString()}</strong>
          </div>
          <div className="document-stat">
            <span>TOKENS · CL100K_BASE</span>
            <strong>{docInfo.token_count.toLocaleString()}</strong>
          </div>
          <p className="document-preview">Preview: {docInfo.preview}</p>
        </div>
      )}
    </section>
  )
}
