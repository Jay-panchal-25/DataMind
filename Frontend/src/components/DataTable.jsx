export default function DataTable({ table }) {
  if (!table || !Array.isArray(table.columns) || !Array.isArray(table.rows)) {
    return <p>Invalid table data</p>;
  }

  const formatCell = (value) => {
    if (value === null || value === undefined) return "-";
    if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(2);
    return String(value);
  };

  return (
    <div className="w-full space-y-2">
      {table.title ? (
        <p className="text-sm font-semibold text-neutral-200">{table.title}</p>
      ) : null}

      <div className="border border-neutral-700 rounded-xl bg-neutral-950/70 shadow-sm">
        <table className="w-full text-sm table-auto">
          <thead className="bg-neutral-900">
            <tr>
              {table.columns.map((col) => (
                <th
                  key={col}
                  className="px-3 py-2 text-left font-semibold text-neutral-200 border-b border-neutral-700"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {table.rows.map((row, idx) => (
              <tr
                key={idx}
                className={`${idx % 2 === 0 ? "bg-neutral-950/50" : "bg-neutral-900/60"} border-t border-neutral-800`}
              >
                {table.columns.map((col) => (
                  <td
                    key={`${idx}-${col}`}
                    className="px-3 py-2 text-neutral-200 align-top break-words"
                  >
                    {formatCell(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

