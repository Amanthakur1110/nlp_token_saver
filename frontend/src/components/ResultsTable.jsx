/**
 * ResultsTable – one row per technique result + one row for the chain.
 *
 * Props:
 *   report      – full report JSON from /api/compress
 */
export default function ResultsTable({ report }) {
  if (!report) return null

  // Collect rows: individual results first, then chain summary
  const rows = []

  if (report.individual) {
    for (const r of report.individual) {
      rows.push({ ...r, _source: 'individual' })
    }
  }

  if (report.chain) {
    // Show a single "Combined chain" row using the last chain step's metrics
    const lastStep = [...report.chain].reverse().find(r => !r.skipped)
    if (lastStep && report.chain_summary) {
      rows.push({
        technique_id: '__chain__',
        technique_name: 'Combined Chain',
        _source: 'chain',
        metrics: {
          tokens_before: report.chain_summary.tokens_before,
          tokens_after: report.chain_summary.tokens_after,
          percent_saved: pct(report.chain_summary.tokens_before, report.chain_summary.tokens_after),
          semantic_similarity: lastStep.metrics?.semantic_similarity,
          entity_retention: lastStep.metrics?.entity_retention,
          number_retention: lastStep.metrics?.number_retention,
          rouge_l: lastStep.metrics?.rouge_l,
          time_ms: report.chain?.reduce((s, r) => s + (r.metrics?.time_ms || 0), 0),
        },
        output_text: report.chain_summary.final_text,
        diff: report.chain_summary.diff,
      })
    }
  }

  if (rows.length === 0) return <p className="empty-results">No results.</p>

  return (
    <section className="data-panel" aria-labelledby="results-table-heading">
      <div className="data-panel-heading">
        <h3 id="results-table-heading">Performance breakdown</h3>
      </div>
      <div className="table-wrap">
        <table className="results-table">
          <thead>
            <tr>
              <th>Technique</th>
              <th>Tokens before</th>
              <th>Tokens after</th>
              <th>Saved</th>
              <th>Similarity</th>
              <th>Entity ret.</th>
              <th>Num. ret.</th>
              <th>ROUGE-L</th>
              <th>Time (ms)</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => {
              if (row.skipped) {
                return (
                  <tr key={row.technique_id} className="skipped-row">
                    <td colSpan={9}>{row.technique_id} – skipped: {row.reason}</td>
                  </tr>
                )
              }
              const m = row.metrics || {}
              return (
                <tr
                  key={`${row._source}_${row.technique_id}`}
                  className={row._source === 'chain' ? 'chain-row' : ''}
                >
                  <td>{row.technique_name}</td>
                  <td>{m.tokens_before ?? '—'}</td>
                  <td>{m.tokens_after ?? '—'}</td>
                  <td>{m.percent_saved != null ? `${m.percent_saved}%` : '—'}</td>
                  <td>{m.semantic_similarity != null ? m.semantic_similarity.toFixed(3) : '—'}</td>
                  <td>{m.entity_retention != null ? `${m.entity_retention}%` : '—'}</td>
                  <td>{m.number_retention != null ? `${m.number_retention}%` : '—'}</td>
                  <td>{m.rouge_l != null ? m.rouge_l.toFixed(3) : '—'}</td>
                  <td>{m.time_ms != null ? m.time_ms.toFixed(1) : '—'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function pct(before, after) {
  if (!before) return 0
  return parseFloat(((1 - after / before) * 100).toFixed(2))
}
