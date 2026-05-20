export default function PredictionCard({ data }) {
  if (!data) return null;

  const {
    input_values,
    model,
    task_type,
    target,
    metrics,
    predictions,
    feature_importance,
    quality_warnings,
    training_rows,
    validation_rows,
  } = data;

  return (
    <div className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.32)]">
      <div className="border-b border-[#17301d] pb-4">
        <p className="text-xs uppercase tracking-[0.28em] text-[#6d8d73]">
          Prediction result
        </p>
        <h2 className="mt-2 text-xl font-semibold text-white">{model}</h2>
        <p className="mt-3 text-sm text-[#badfc0]">
          Task: <span className="text-white">{task_type}</span>
        </p>
        <p className="mt-1 text-sm text-[#badfc0]">
          Target: <span className="text-white">{target}</span>
        </p>
        <p className="mt-1 text-sm text-[#badfc0]">
          Training rows: <span className="text-white">{training_rows ?? 0}</span>
        </p>
        <p className="mt-1 text-sm text-[#badfc0]">
          Validation rows: <span className="text-white">{validation_rows ?? 0}</span>
        </p>
      </div>

      {metrics && (
        <div className="mt-5 grid gap-3 sm:grid-cols-2">
          {Object.entries(metrics).map(([key, value]) => (
            <div
              key={key}
              className="rounded-2xl border border-[#17301d] bg-[#050a05] px-4 py-3"
            >
              <p className="text-xs uppercase tracking-[0.24em] text-[#6d8d73]">
                {key}
              </p>
              <p className="mt-2 text-lg font-semibold text-white">
                {typeof value === "number" ? value.toFixed(4) : value}
              </p>
            </div>
          ))}
        </div>
      )}

      {predictions && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-[#7da684]">
            Predictions
          </h3>
          <div className="mt-3 max-h-48 overflow-y-auto rounded-2xl border border-[#17301d] bg-[#050a05] p-3">
            {Array.isArray(predictions) ? (
              predictions.map((prediction, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between gap-4 border-b border-[#112015] py-2 text-sm last:border-b-0"
                >
                  <span className="text-[#7fa486]">Row {index + 1}</span>
                  <span className="font-medium text-white">{prediction}</span>
                </div>
              ))
            ) : (
              <pre className="text-sm text-[#d8f2dc]">
                {JSON.stringify(predictions, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}

      {input_values && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-[#7da684]">
            Input values
          </h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {Object.entries(input_values).map(([key, value]) => (
              <div
                key={key}
                className="rounded-2xl border border-[#17301d] bg-[#050a05] px-4 py-3"
              >
                <p className="text-xs uppercase tracking-[0.24em] text-[#6d8d73]">
                  {key}
                </p>
                <p className="mt-2 text-base font-medium text-white">{String(value)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {feature_importance && Object.keys(feature_importance).length > 0 && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-[#7da684]">
            Feature importance
          </h3>
          <div className="mt-3 space-y-3">
            {Object.entries(feature_importance).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="truncate text-[#d8f2dc]">{key}</span>
                  <span className="text-[#8bb292]">
                    {Number(value).toFixed(4)}
                  </span>
                </div>
                <div className="overflow-hidden rounded-full bg-[#122015]">
                  <div
                    className="h-3 rounded-full bg-gradient-to-r from-[#1faa59] to-[#59d98c]"
                    style={{ width: `${Math.min(Number(value) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {quality_warnings?.length > 0 && (
        <div className="mt-5 rounded-2xl border border-[#3f3120] bg-[#171007] p-4 text-sm text-[#ffd8ab]">
          {quality_warnings.map((warning, index) => (
            <p key={index}>{warning}</p>
          ))}
        </div>
      )}
    </div>
  );
}
