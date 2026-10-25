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
    <div className="border border-gray-300 p-4 mb-4 bg-white">
      <h2 className="font-bold text-lg mb-3">2. Select Techniques</h2>

      {/* Preset buttons */}
      <div className="flex gap-2 mb-4">
        <span className="text-sm self-center text-gray-600">Presets:</span>
        {PRESETS.map(p => (
          <button
            key={p}
            onClick={() => onPreset(p)}
            className="border border-gray-400 px-2 py-0.5 text-xs bg-gray-100 hover:bg-gray-200"
          >
            {p.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Technique list */}
      <div className="space-y-3">
        {techniques.map(t => {
          const sel = selected[t.id] || {}
          const isChecked = !!sel.checked
          const isDisabled = !t.available

          return (
            <div
              key={t.id}
              className={`border p-3 ${isDisabled ? 'border-gray-200 bg-gray-50 opacity-60' : 'border-gray-300'}`}
            >
              {/* Header row */}
              <label className="flex items-start gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  disabled={isDisabled}
                  checked={isChecked}
                  onChange={() => onToggle(t.id)}
                  className="mt-0.5"
                />
                <div>
                  <span className="font-medium text-sm">{t.name}</span>
                  {isDisabled && (
                    <span className="ml-2 text-xs text-gray-500">
                      (unavailable: {t.unavailable_reason})
                    </span>
                  )}
                  <p className="text-xs text-gray-600 mt-0.5">{t.description}</p>
                </div>
              </label>

              {/* Parameter controls – only when checked and available */}
              {isChecked && !isDisabled && t.params_schema.length > 0 && (
                <div className="mt-2 ml-5 space-y-2">
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

      <button
        onClick={onRun}
        disabled={loading}
        className="mt-4 border border-gray-600 px-4 py-1.5 text-sm bg-gray-800 text-white hover:bg-gray-700 disabled:opacity-50"
      >
        {loading ? 'Running…' : 'Run compression'}
      </button>
    </div>
  )
}

/** Renders a single parameter control based on its schema type. */
function ParamControl({ param, value, onChange }) {
  const label = (
    <label className="text-xs text-gray-700 block mb-0.5">{param.label}</label>
  )

  if (param.type === 'slider') {
    return (
      <div>
        {label}
        <div className="flex items-center gap-2">
          <input
            type="range"
            min={param.min}
            max={param.max}
            step={param.step}
            value={value}
            onChange={e => onChange(parseFloat(e.target.value))}
            className="w-40"
          />
          <span className="text-xs w-8">{value}</span>
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
          className="border border-gray-300 text-xs p-0.5"
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
          className="border border-gray-300 text-xs p-0.5 w-60"
          placeholder={param.default}
        />
      </div>
    )
  }

  return null
}

