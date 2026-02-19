import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ScatterChart,
  Scatter,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const COLORS = {
  primary: "#ff7f0e",
  secondary: "#1f77b4",
  grid: "#e0e0e0",
};

const PIE_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"];

export default function ChartRenderer({ chart }) {
  if (!chart) return null;

  // BAR + LINE + HISTOGRAM
  if (
    chart.chart_type === "bar" ||
    chart.chart_type === "line" ||
    chart.chart_type === "histogram"
  ) {
    const data = chart.labels.map((label, index) => ({
      name: label,
      value: chart.values[index],
    }));

    // HISTOGRAM (just bar chart with no radius + tighter bars)
    if (chart.chart_type === "histogram") {
      return (
        <BarChart width={500} height={300} data={data}>
          <CartesianGrid stroke={COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill={COLORS.primary} />
        </BarChart>
      );
    }

    if (chart.chart_type === "bar") {
      return (
        <BarChart width={500} height={300} data={data}>
          <CartesianGrid stroke={COLORS.grid} strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
        </BarChart>
      );
    }

    return (
      <LineChart width={500} height={300} data={data}>
        <CartesianGrid stroke={COLORS.grid} strokeDasharray="3 3" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="value"
          stroke={COLORS.primary}
          strokeWidth={2}
          dot={{ r: 4 }}
        />
      </LineChart>
    );
  }

  // SCATTER
  if (chart.chart_type === "scatter") {
    const data = chart.x.map((x, i) => ({
      x,
      y: chart.y[i],
    }));

    return (
      <ScatterChart width={500} height={300}>
        <CartesianGrid stroke={COLORS.grid} />
        <XAxis dataKey="x" />
        <YAxis dataKey="y" />
        <Tooltip />
        <Scatter data={data} fill={COLORS.secondary} />
      </ScatterChart>
    );
  }

  // PIE
  // PIE
  if (chart.chart_type === "pie") {
    const data = chart.labels.map((label, index) => ({
      name: label,
      value: chart.values[index],
    }));

    const total = data.reduce((sum, entry) => sum + entry.value, 0);

    const renderCustomLabel = ({ name, value }) => {
      const percent = ((value / total) * 100).toFixed(1);
      return `${name} (${percent}%)`;
    };

    return (
      <PieChart width={500} height={300}>
        <Tooltip />
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label={renderCustomLabel}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={PIE_COLORS[index % PIE_COLORS.length]}
            />
          ))}
        </Pie>
      </PieChart>
    );
  }

  return <p>Unsupported chart type</p>;
}
