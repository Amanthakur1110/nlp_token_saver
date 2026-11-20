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
    <div className="metrics-grid" aria-label="Compression summary">
      <div className="metric-card">
        <span className="metric-label">ORIGINAL TOKENS</span>
        <p className="metric-value">{original_tokens?.toLocaleString()}</p>
      </div>

      {chain_summary && (
        <>
          <div className="metric-card">
            <span className="metric-label">TOKENS AFTER</span>
            <p className="metric-value">{chain_summary.tokens_after?.toLocaleString()}</p>
          </div>
          <div className="metric-card">
            <span className="metric-label">TOKENS SAVED</span>
            <p className="metric-value metric-value-small">
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
