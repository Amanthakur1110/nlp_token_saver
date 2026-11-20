/**
 * DiffView – compare the original (removed words in red) with compressed text.
 * Also shows removed phrases and copy/download actions.
 *
 * Props:
 *   result – one row from the report (has .diff and .output_text)
 */
export default function DiffView({ result }) {
  if (!result || !result.diff) return null

  const { segments = [], removed_list = [] } = result.diff

  function handleCopy() {
    navigator.clipboard.writeText(result.output_text || '')
  }

  function handleDownload() {
    const blob = new Blob([result.output_text || ''], { type: 'text/plain' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${result.technique_id}_compressed.txt`
    a.click()
  }

  return (
    <article className="diff-panel">
      <h3 className="diff-title">{result.technique_name}</h3>
      {result.contextLabel && (
        <p className="diff-context">{result.contextLabel}</p>
      )}

      {/* Two-column diff */}
      <div className="diff-grid">
        {/* Left: original with removed words and phrases highlighted */}
        <div>
          <p className="diff-column-title">Original</p>
          <div className="diff-content">
            {segments.map((seg, i) =>
              seg.status === 'removed' ? (
                <span key={i} className="removed-segment">
                  {seg.text}
                </span>
              ) : (
                <span key={i}>{seg.text}</span>
              )
            )}
          </div>
        </div>

        {/* Right: compressed output */}
        <div>
          <p className="diff-column-title">Compressed</p>
          <div className="diff-content">
            {result.output_text}
          </div>
        </div>
      </div>

      {/* Removed content list */}
      {removed_list.length > 0 && (
        <div className="removed-section">
          <p className="diff-column-title">
            Removed words and phrases ({removed_list.length})
          </p>
          <ul className="removed-list">
            {removed_list.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
      {removed_list.length === 0 && (
        <p className="no-removals">No words or phrases were removed by this result.</p>
      )}

      {/* Actions */}
      <div className="action-row">
        <button
          onClick={handleCopy}
          className="action-button"
        >
          Copy compressed text
        </button>
        <button
          onClick={handleDownload}
          className="action-button"
        >
          Download .txt
        </button>
      </div>
    </article>
  )
}
