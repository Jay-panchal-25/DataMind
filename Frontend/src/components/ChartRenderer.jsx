export default function ChartRenderer({ data }) {
  if (!data) return null;

  if (data.image) {
    return (
      <div className="overflow-hidden rounded-[24px] border border-[#17301d] bg-[#071007] p-4 shadow-[0_16px_40px_rgba(0,0,0,0.32)]">
        <img
          src={`data:image/png;base64,${data.image}`}
          alt="chart"
          className="w-full rounded-[18px]"
        />
      </div>
    );
  }

  const { chart_type, labels, values, x, y } = data;

  return (
    <div className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5 shadow-[0_16px_40px_rgba(0,0,0,0.32)]">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[#6d8d73]">
            Visualization
          </p>
          <h2 className="mt-2 text-lg font-semibold capitalize text-white">
            {chart_type} chart
          </h2>
        </div>
      </div>

      {(chart_type === "bar" ||
        chart_type === "pie" ||
        chart_type === "histogram") && (
        <SimpleBar labels={labels || []} values={values || []} />
      )}

      {chart_type === "line" && <LineChart values={values || []} />}

      {chart_type === "scatter" && <ScatterPlot x={x || []} y={y || []} />}
    </div>
  );
}

function SimpleBar({ labels, values }) {
  if (!labels.length || !values.length) {
    return <p className="text-sm text-[#7a977f]">No data to display.</p>;
  }

  const max = Math.max(...values, 1);

  return (
    <div className="space-y-3">
      {labels.map((label, index) => (
        <div key={index} className="grid grid-cols-[120px_1fr_72px] items-center gap-3">
          <div className="truncate text-sm text-[#cfead4]">{label}</div>
          <div className="h-3 rounded-full bg-[#122015]">
            <div
              className="h-3 rounded-full bg-gradient-to-r from-[#1faa59] to-[#59d98c]"
              style={{ width: `${(values[index] / max) * 100}%` }}
            />
          </div>
          <div className="text-right text-sm text-[#8bb292]">{values[index]}</div>
        </div>
      ))}
    </div>
  );
}

function LineChart({ values }) {
  if (!values.length) {
    return <p className="text-sm text-[#7a977f]">No data to display.</p>;
  }

  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);

  return (
    <div className="flex h-48 items-end gap-2 rounded-[20px] border border-[#17301d] bg-[#050a05] p-4">
      {values.map((value, index) => (
        <div
          key={index}
          className="flex-1 rounded-t-full bg-gradient-to-t from-[#14783b] to-[#59d98c]"
          style={{ height: `${((value - min) / (max - min || 1)) * 100}%` }}
        />
      ))}
    </div>
  );
}

function ScatterPlot({ x, y }) {
  if (!x.length || !y.length) {
    return <p className="text-sm text-[#7a977f]">No data to display.</p>;
  }

  const maxX = Math.max(...x, 1);
  const maxY = Math.max(...y, 1);

  return (
    <div className="relative h-64 w-full rounded-[20px] border border-[#17301d] bg-[linear-gradient(180deg,#081008,#020402)]">
      {x.map((_, index) => (
        <div
          key={index}
          className="absolute h-3 w-3 -translate-x-1/2 translate-y-1/2 rounded-full border border-[#dffff0] bg-[#59d98c] shadow-[0_0_18px_rgba(89,217,140,0.45)]"
          style={{
            left: `${(x[index] / maxX) * 100}%`,
            bottom: `${(y[index] / maxY) * 100}%`,
          }}
        />
      ))}
    </div>
  );
}
