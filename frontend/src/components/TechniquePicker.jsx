/**
 * TechniquePicker – checkboxes + auto-generated parameter controls.
 *
 * Props:
 *   techniques   – array from GET /api/techniques
 *   selected     – { [id]: {checked, params} }
 *   onToggle(id) – toggle checkbox
 *   onParam(id, paramName, value) – update a param value
 *   onRun()      – fire the run
 *   onPreset(name) – apply a preset
 *   loading      – bool
 */
export default function TechniquePicker({
  techniques, selected, onToggle, onParam, onRun, onPreset, loading
}) {
  const PRESETS = ['safe', 'balanced', 'max_saver']

  return (
    <section className="panel" aria-labelledby="techniques-heading">
      <div className="panel-heading">
        <span className="step-number">02</span>
        <div>
          <h2 id="techniques-heading" className="panel-title">Choose your approach</h2>
          <p className="panel-subtitle">Combine techniques or start from a preset.</p>
        </div>
      </div>

      {/* Preset buttons */}
      <div className="preset-row">
        <span className="preset-label">QUICK START</span>
        {PRESETS.map(p => (
          <button
            key={p}
            onClick={() => onPreset(p)}
            disabled={loading}
            className="preset-button"
          >
            {p.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Technique list */}
      <div className="technique-list">
        {techniques.map(t => {
          const sel = selected[t.id] || {}
          const isChecked = !!sel.checked
          const isDisabled = !t.available

          return (
            <div
              key={t.id}
              className={`technique-card ${isChecked ? 'is-selected' : ''} ${isDisabled ? 'is-unavailable' : ''}`}
            >
              {/* Header row */}
              <label className="technique-label">
                <input
                  type="checkbox"
                  disabled={isDisabled}
                  checked={isChecked}
                  onChange={() => onToggle(t.id)}
                  className="technique-checkbox"
                />
                <div>
                  <span className="technique-name">{t.name}</span>
                  {isDisabled && (
                    <span className="unavailable-note">
                      · Unavailable: {t.unavailable_reason}
                    </span>
                  )}
                  <p className="technique-description">{t.description}</p>
                </div>
              </label>

              {/* Parameter controls – only when checked and available */}
              {isChecked && !isDisabled && t.params_schema.length > 0 && (
                <div className="param-list">
                  {t.params_schema.map(param => (
                    <ParamControl
                      key={param.name}
                      param={param}
                      value={sel.params?.[param.name] ?? param.default}
                      onChange={val => onParam(t.id, param.name, val)}
                    />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="run-row">
        <span className="run-hint">Your original document stays unchanged.</span>
        <button onClick={onRun} disabled={loading} className="primary-button">
          {loading && <span className="spinner" aria-hidden="true" />}
          {loading ? 'Compressing…' : 'Run compression'}
        </button>
      </div>
    </section>
  )
}

/** Renders a single parameter control based on its schema type. */
function ParamControl({ param, value, onChange }) {
  const label = (
    <label className="param-label">{param.label}</label>
  )

  if (param.type === 'slider') {
    return (
      <div>
        {label}
        <div className="range-row">
          <input
            type="range"
            min={param.min}
            max={param.max}
            step={param.step}
            value={value}
            onChange={e => onChange(parseFloat(e.target.value))}
          />
          <span className="range-value">{value}</span>
        </div>
      </div>
    )
  }

  if (param.type === 'select') {
    return (
      <div>
        {label}
        <select
          value={value}
          onChange={e => onChange(parseInt(e.target.value))}
          className="param-control"
        >
          {param.options.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
    )
  }

  if (param.type === 'text') {
    return (
      <div>
        {label}
        <input
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          className="param-control"
          placeholder={param.default}
        />
      </div>
    )
  }

  return null
}
