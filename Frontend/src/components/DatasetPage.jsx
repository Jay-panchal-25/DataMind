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
    <div className="min-h-screen bg-neutral-900 p-8">
      <div className="max-w-7xl mx-auto bg-neutral-800 shadow-lg rounded-xl p-6">
        <h2 className="text-2xl font-semibold text-white mb-6">
          Uploaded Dataset
        </h2>

        {data.length === 0 ? (
          <p className="text-white">No data available</p>
        ) : (
          <div className="overflow-x-auto border rounded-lg">
            <table className="min-w-full text-sm text-left text-white">
              <thead className="bg-neutral-900 text-white uppercase text-xs">
                <tr>
                  {columns.map((col) => (
                    <th key={col} className="px-4 py-3 border-b">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-200">
                {data.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition">
                    {columns.map((col) => (
                      <td key={col} className="px-4 py-2 whitespace-nowrap">
                        {row[col]}
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
            className={`px-4 py-2 rounded-lg text-sm font-medium transition
              ${
                page === 1
                  ? "bg-white text-black cursor-not-allowed"
                  : "bg-gray-600 text-white hover:bg-gray-700"
              }`}
          >
            Previous
          </button>

          <span className="text-white text-sm">
            Page {page} of {totalPages}
          </span>

          <button
            onClick={() => setPage((prev) => prev + 1)}
            disabled={page === totalPages}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition
              ${
                page === totalPages
                  ? "bg-white text-black cursor-not-allowed"
                  : "bg-gray-600 text-white hover:bg-gray-700"
              }`}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
