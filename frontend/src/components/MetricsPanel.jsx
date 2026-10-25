/**
 * MetricsPanel – compact summary card shown above the results table.
 * Shows original token count and chain final count if available.
 *
 * Props:
 *   report – full report JSON
 */
export default function MetricsPanel({ report }) {
  if (!report) return null

  const { original_tokens, chain_summary } = report

  return (
    <div className="border border-gray-300 bg-white p-4 mb-4 flex gap-8 text-sm">
      <div>
        <span className="text-gray-600 text-xs">Original tokens</span>
        <p className="font-bold text-lg">{original_tokens?.toLocaleString()}</p>
      </div>

      {chain_summary && (
        <>
          <div>
            <span className="text-gray-600 text-xs">After chain</span>
            <p className="font-bold text-lg">{chain_summary.tokens_after?.toLocaleString()}</p>
          </div>
          <div>
            <span className="text-gray-600 text-xs">Chain saved</span>
            <p className="font-bold text-lg text-green-700">
              {pct(chain_summary.tokens_before, chain_summary.tokens_after)}%
            </p>
          </div>
        </>
      )}
    </div>
  )
}

function pct(before, after) {
  if (!before) return 0
  return ((1 - after / before) * 100).toFixed(1)
}

