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
    <div className="flex h-full bg-neutral-900 text-white">
      {/* GRAPH AREA */}
      <div className="flex-1 p-6">
        <h2 className="text-2xl font-bold mb-6">Graph Builder</h2>

        {error && <div className="bg-red-600 p-3 rounded mb-4">{error}</div>}

        <div className="bg-neutral-700 rounded-xl p-6 h-[500px]">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              Loading...
            </div>
          ) : (
            <>
              <h3 className="text-lg font-semibold text-center mb-4">
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
      <div className="w-80 bg-neutral-800 border-l border-neutral-700 p-6">
        <h3 className="text-lg font-semibold mb-6">Settings</h3>

        <div className="mb-5">
          <label className="block mb-2">Chart Type</label>
          <select
            className="w-full bg-neutral-700 p-2 rounded"
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
          <label className="block mb-2">
            {chartType === "histogram" ? "Column" : "X Axis"}
          </label>
          <select
            className="w-full bg-neutral-700 p-2 rounded"
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
            <label className="block mb-2">Y Axis</label>
            <select
              className="w-full bg-neutral-700 p-2 rounded"
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
          className="w-full bg-white hover:bg-gray-200 text-black py-2 rounded-lg"
        >
          Generate
        </button>
      </div>
    </div>
  );
}
