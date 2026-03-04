import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
  Label,
} from "recharts";

export default function GraphPage() {
  const [columns, setColumns] = useState([]);
  const [chartType, setChartType] = useState("bar");
  const [xColumn, setXColumn] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [data, setData] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

  useEffect(() => {
    fetch("http://localhost:8000/columns")
      .then((res) => res.json())
      .then((data) => setColumns(data.columns || []));
  }, []);

  const generateGraph = async () => {
    // Histogram only needs X
    if (chartType === "histogram") {
      if (!xColumn) {
        setError("Please select a column");
        return;
      }
    } else {
      if (!xColumn || !yColumn) {
        setError("Please select both X and Y columns");
        return;
      }
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/generate-graph", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chart_type: chartType,
          x: xColumn,
          y: chartType === "histogram" ? null : yColumn,
        }),
      });

      const result = await res.json();

      if (result.error) {
        setError(result.error);
        setData([]);
      } else {
        // Histogram comes as raw array
        if (chartType === "histogram") {
          const formatted = result.data.map((value) => ({
            value: value,
          }));
          setData(formatted);
        } else {
          setData(result.data || []);
        }
      }
    } catch (err) {
      setError("Server error");
      setData([]);
    }

    setLoading(false);
  };

  const chartTitle =
    chartType === "histogram"
      ? `Histogram of ${xColumn}`
      : xColumn && yColumn
        ? `${chartType.toUpperCase()} Chart of ${yColumn} vs ${xColumn}`
        : "Graph Preview";

  return (
    <div className="flex h-full bg-transparent text-neutral-200">
      {/* GRAPH AREA */}
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-extrabold mb-6 text-neutral-100">Graph Builder</h2>

        {error && <div className="bg-rose-950/30 border border-rose-700 text-rose-300 p-3 rounded-lg mb-4">{error}</div>}

        <div className="bg-neutral-900 border border-neutral-800 shadow-sm rounded-2xl p-6 h-[500px]">
          {loading ? (
            <div className="flex items-center justify-center h-full text-neutral-400">
              Loading...
            </div>
          ) : (
            <>
              <h3 className="text-lg font-semibold text-center text-neutral-200 mb-4">
                {chartTitle}
              </h3>

              <ResponsiveContainer width="100%" height="90%">
                {chartType === "bar" && (
                  <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={xColumn} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey={yColumn} fill="#3b82f6" />
                  </BarChart>
                )}

                {chartType === "line" && (
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey={xColumn} />
                    <YAxis />
                    <Tooltip />
                    <Line dataKey={yColumn} stroke="#10b981" />
                  </LineChart>
                )}

                {chartType === "pie" && (
                  <PieChart>
                    <Tooltip />
                    <Pie
                      data={data}
                      dataKey={yColumn}
                      nameKey={xColumn}
                      outerRadius={150}
                      label
                    >
                      {data.map((_, index) => (
                        <Cell
                          key={index}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                )}

                {chartType === "scatter" && (
                  <ScatterChart>
                    <CartesianGrid />
                    <XAxis dataKey={xColumn} />
                    <YAxis dataKey={yColumn} />
                    <Tooltip />
                    <Scatter data={data} fill="#f59e0b" />
                  </ScatterChart>
                )}

                {chartType === "histogram" && (
                  <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="value" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#8b5cf6" />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </>
          )}
        </div>
      </div>

      {/* RIGHT SIDEBAR */}
      <div className="w-80 bg-neutral-900 border-l border-neutral-800 p-6">
        <h3 className="text-lg font-bold text-neutral-100 mb-6">Settings</h3>

        <div className="mb-5">
          <label className="block mb-2 text-sm font-semibold text-neutral-400">Chart Type</label>
          <select
            className="w-full bg-neutral-950 border border-neutral-700 p-2.5 rounded-lg text-neutral-200"
            value={chartType}
            onChange={(e) => {
              setChartType(e.target.value);
              setData([]);
              setError("");
            }}
          >
            <option value="bar">Bar</option>
            <option value="line">Line</option>
            <option value="pie">Pie</option>
            <option value="scatter">Scatter</option>
            <option value="histogram">Histogram</option>
          </select>
        </div>

        <div className="mb-5">
          <label className="block mb-2 text-sm font-semibold text-neutral-400">
            {chartType === "histogram" ? "Column" : "X Axis"}
          </label>
          <select
            className="w-full bg-neutral-950 border border-neutral-700 p-2.5 rounded-lg text-neutral-200"
            value={xColumn}
            onChange={(e) => setXColumn(e.target.value)}
          >
            <option value="">Select</option>
            {columns.map((col) => (
              <option key={col} value={col}>
                {col}
              </option>
            ))}
          </select>
        </div>

        {/* Hide Y for histogram */}
        {chartType !== "histogram" && (
          <div className="mb-5">
            <label className="block mb-2 text-sm font-semibold text-neutral-400">Y Axis</label>
            <select
              className="w-full bg-neutral-950 border border-neutral-700 p-2.5 rounded-lg text-neutral-200"
              value={yColumn}
              onChange={(e) => setYColumn(e.target.value)}
            >
              <option value="">Select</option>
              {columns.map((col) => (
                <option key={col} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={generateGraph}
          className="w-full bg-white hover:bg-neutral-200 text-neutral-900 py-2.5 rounded-lg font-semibold"
        >
          Generate
        </button>
      </div>
    </div>
  );
}

