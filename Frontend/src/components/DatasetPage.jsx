import { useEffect, useState } from "react";

export default function DatasetPage() {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const pageSize = 10;

  useEffect(() => {
    fetch(`http://localhost:8000/dataset?page=${page}&page_size=${pageSize}`)
      .then((res) => res.json())
      .then((res) => {
        setData(res.data || []);
        setColumns(res.columns || []);
        setTotalPages(res.total_pages || 1);
      })
      .catch((err) => console.error(err));
  }, [page]);

  return (
    <div className="min-h-screen p-8 bg-transparent">
      <div className="max-w-7xl mx-auto bg-neutral-900 shadow-xl rounded-2xl border border-neutral-800 p-6">
        <h2 className="text-2xl font-extrabold text-neutral-100 mb-6">
          Uploaded Dataset
        </h2>

        {data.length === 0 ? (
          <p className="text-neutral-400">No data available</p>
        ) : (
          <div className="overflow-x-auto border border-neutral-700 rounded-xl">
            <table className="min-w-full text-sm text-left text-neutral-200">
              <thead className="bg-neutral-950 text-neutral-400 uppercase text-xs">
                <tr>
                  {columns.map((col) => (
                    <th
                      key={col}
                      className="px-4 py-3 border-b border-neutral-700"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-neutral-800">
                {data.map((row, index) => (
                  <tr key={index} className="hover:bg-neutral-800/70 transition">
                    {columns.map((col) => (
                      <td
                        key={col}
                        className="px-4 py-2 whitespace-nowrap text-neutral-300"
                      >
                        {row[col] === null || row[col] === undefined
                          ? "Unknown"
                          : typeof row[col] === "boolean"
                            ? row[col].toString()
                            : row[col]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={() => setPage((prev) => prev - 1)}
            disabled={page === 1}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              page === 1
                ? "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                : "bg-white text-neutral-900 hover:bg-neutral-200"
            }`}
          >
            Previous
          </button>

          <span className="text-neutral-300 text-sm font-semibold">
            Page {page} of {totalPages}
          </span>

          <button
            onClick={() => setPage((prev) => prev + 1)}
            disabled={page === totalPages}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              page === totalPages
                ? "bg-neutral-800 text-neutral-500 cursor-not-allowed"
                : "bg-white text-neutral-900 hover:bg-neutral-200"
            }`}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

