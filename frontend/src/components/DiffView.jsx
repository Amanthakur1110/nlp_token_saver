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
    <div className="border border-gray-300 bg-white p-4 mb-4">
      <h2 className="font-bold text-lg mb-3">
        4. Detail: {result.technique_name}
      </h2>

      {/* Two-column diff */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Left: original with removed words and phrases highlighted */}
        <div>
          <p className="text-xs font-semibold text-gray-600 mb-1">Original</p>
          <div className="border border-gray-200 p-3 text-xs leading-relaxed max-h-64 overflow-y-auto whitespace-pre-wrap break-words">
            {segments.map((seg, i) =>
              seg.status === 'removed' ? (
                <span key={i} className="bg-red-100 text-red-700 rounded">
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
          <p className="text-xs font-semibold text-gray-600 mb-1">Compressed</p>
          <div className="border border-gray-200 p-3 text-xs leading-relaxed max-h-64 overflow-y-auto whitespace-pre-wrap">
            {result.output_text}
          </div>
        </div>
      </div>

      {/* Removed content list */}
      {removed_list.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-600 mb-1">
            Removed words and phrases ({removed_list.length})
          </p>
          <ul className="border border-gray-200 p-2 max-h-32 overflow-y-auto text-xs space-y-1">
            {removed_list.map((s, i) => (
              <li key={i} className="text-red-700 bg-red-50 px-1 rounded">{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={handleCopy}
          className="border border-gray-400 px-2 py-0.5 text-xs bg-gray-100 hover:bg-gray-200"
        >
          Copy compressed text
        </button>
        <button
          onClick={handleDownload}
          className="border border-gray-400 px-2 py-0.5 text-xs bg-gray-100 hover:bg-gray-200"
        >
          Download .txt
        </button>
      </div>
    </div>
  )
}
