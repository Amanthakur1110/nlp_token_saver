import { useState, useEffect } from 'react'
import { fetchTechniques, runCompress, runPreset } from './api'
import UploadPanel from './components/UploadPanel'
import TechniquePicker from './components/TechniquePicker'
import ResultsTable from './components/ResultsTable'
import DiffView from './components/DiffView'
import MetricsPanel from './components/MetricsPanel'

export default function App() {
  // ── state ──────────────────────────────────────────────────────────────────
  const [techniques, setTechniques] = useState([])
  const [techniquesLoading, setTechniquesLoading] = useState(true)
  const [techError, setTechError]   = useState('')

  const [docInfo, setDocInfo]     = useState(null)  // from upload

  // selected: { [technique_id]: { checked: bool, params: {} } }
  const [selected, setSelected]   = useState({})

  const [loading, setLoading]     = useState(false)
  const [runError, setRunError]   = useState('')
  const [report, setReport]       = useState(null)

  // ── load techniques on mount ───────────────────────────────────────────────
  useEffect(() => {
    fetchTechniques()
      .then(list => {
        setTechniques(list)
        // Initialise selected state with defaults from schema
        const init = {}
        for (const t of list) {
          const params = {}
          for (const p of t.params_schema) params[p.name] = p.default
          init[t.id] = { checked: false, params }
        }
        setSelected(init)
      })
      .catch(e => setTechError(e.message))
      .finally(() => setTechniquesLoading(false))
  }, [])

  // ── handlers ───────────────────────────────────────────────────────────────

  function handleToggle(id) {
    setSelected(s => ({
      ...s,
      [id]: { ...s[id], checked: !s[id]?.checked },
    }))
  }

  function handleParam(id, name, value) {
    setSelected(s => ({
      ...s,
      [id]: { ...s[id], params: { ...s[id]?.params, [name]: value } },
    }))
  }

  async function handleRun() {
    if (!docInfo) { setRunError('Please upload a document first.'); return }
    const picks = Object.entries(selected)
      .filter(([, v]) => v.checked)
      .map(([id, v]) => ({ id, params: v.params }))
    if (picks.length === 0) { setRunError('Select at least one technique.'); return }

    setLoading(true)
    setRunError('')
    setReport(null)

    try {
      const result = await runCompress(docInfo.doc_id, picks, 'both')
      setReport(result)
    } catch (e) {
      setRunError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handlePreset(preset) {
    if (!docInfo) { setRunError('Please upload a document first.'); return }

    setLoading(true)
    setRunError('')
    setReport(null)

    try {
      const result = await runPreset(docInfo.doc_id, preset)
      setReport(result)
      // Reflect preset selections in the checkboxes
      // (we'd need preset tech lists from the server; skip for now – just show results)
    } catch (e) {
      setRunError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // ── render ─────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-5xl mx-auto p-4">

      {/* Header */}
      <header className="border-b border-gray-300 pb-3 mb-4">
        <h1 className="text-2xl font-bold">TokenSaver</h1>
        <p className="text-sm text-gray-600">
          Upload a document, apply token-saving techniques, see how many tokens were saved.
        </p>
      </header>

      {/* Upload */}
      <UploadPanel onUploaded={setDocInfo} />

      {/* Technique picker */}
      {techError && (
        <div className="border border-red-400 bg-red-50 text-red-700 p-2 text-sm mb-4">{techError}</div>
      )}
      {techniquesLoading && (
        <p className="text-sm text-gray-600 mb-4" role="status" aria-live="polite">
          Loading compression techniques…
        </p>
      )}
      {techniques.length > 0 && (
        <TechniquePicker
          techniques={techniques}
          selected={selected}
          onToggle={handleToggle}
          onParam={handleParam}
          onRun={handleRun}
          onPreset={handlePreset}
          loading={loading}
        />
      )}

      {/* Run error */}
      {runError && (
        <div className="border border-red-400 bg-red-50 text-red-700 p-2 text-sm mb-4">{runError}</div>
      )}

      {/* Results */}
      {report && (
        <>
          <MetricsPanel report={report} />
          <ResultsTable report={report} />
          <section aria-labelledby="technique-details-heading">
            <h2 id="technique-details-heading" className="font-bold text-lg mb-3">
              4. Technique-by-technique outputs
            </h2>
            {getTechniqueDetails(report).map(result => (
              <DiffView key={`${result._source}_${result.technique_id}`} result={result} />
            ))}
          </section>
        </>
      )}
    </div>
  )
}

function getTechniqueDetails(report) {
  const individualResults = (report.individual || [])
    .filter(result => !result.skipped)
    .map(result => ({
      ...result,
      _source: 'individual',
      contextLabel: 'Independent result using the uploaded document as input.',
    }))

  const hasSuccessfulChainStep = (report.chain || []).some(result => !result.skipped)
  const combinedResult = report.chain_summary && hasSuccessfulChainStep
    ? [{
        technique_id: '__chain__',
        technique_name: 'Combined Chain',
        output_text: report.chain_summary.final_text,
        diff: report.chain_summary.diff,
        _source: 'chain-summary',
        contextLabel: 'Final output after all techniques in the chain have been applied.',
      }]
    : []

  return [...individualResults, ...combinedResult]
}
