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

  if (rows.length === 0) return <p className="text-sm text-gray-500">No results.</p>

  return (
    <div className="border border-gray-300 bg-white mb-4 overflow-x-auto">
      <h2 className="font-bold text-lg p-4 border-b border-gray-200">3. Results</h2>
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr className="bg-gray-100 text-left">
            <th className="p-2 border-b border-gray-200">Technique</th>
            <th className="p-2 border-b border-gray-200">Tokens before</th>
            <th className="p-2 border-b border-gray-200">Tokens after</th>
            <th className="p-2 border-b border-gray-200">% Saved</th>
            <th className="p-2 border-b border-gray-200">Similarity</th>
            <th className="p-2 border-b border-gray-200">Entity ret.</th>
            <th className="p-2 border-b border-gray-200">Num. ret.</th>
            <th className="p-2 border-b border-gray-200">ROUGE-L</th>
            <th className="p-2 border-b border-gray-200">Time (ms)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => {
            if (row.skipped) {
              return (
                <tr key={row.technique_id} className="opacity-50">
                  <td className="p-2 border-b border-gray-100" colSpan={9}>
                    {row.technique_id} – skipped: {row.reason}
                  </td>
                </tr>
              )
            }
            const m = row.metrics || {}
            return (
              <tr
                key={`${row._source}_${row.technique_id}`}
                className={`border-b border-gray-100 ${row._source === 'chain' ? 'font-semibold' : ''}`}
              >
                <td className="p-2">{row.technique_name}</td>
                <td className="p-2">{m.tokens_before ?? '—'}</td>
                <td className="p-2">{m.tokens_after ?? '—'}</td>
                <td className="p-2">{m.percent_saved != null ? `${m.percent_saved}%` : '—'}</td>
                <td className="p-2">{m.semantic_similarity != null ? m.semantic_similarity.toFixed(3) : '—'}</td>
                <td className="p-2">{m.entity_retention != null ? `${m.entity_retention}%` : '—'}</td>
                <td className="p-2">{m.number_retention != null ? `${m.number_retention}%` : '—'}</td>
                <td className="p-2">{m.rouge_l != null ? m.rouge_l.toFixed(3) : '—'}</td>
                <td className="p-2">{m.time_ms != null ? m.time_ms.toFixed(1) : '—'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function pct(before, after) {
  if (!before) return 0
  return parseFloat(((1 - after / before) * 100).toFixed(2))
}
