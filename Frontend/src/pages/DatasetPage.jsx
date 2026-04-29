import { useEffect, useState } from "react";
import { getDataset } from "../services/app";

export default function DatasetPage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let ignore = false;

    getDataset().then((res) => {
      if (!ignore) {
        setData(res.data);
      }
    });

    return () => {
      ignore = true;
    };
  }, []);

  if (!data) return <div>Loading...</div>;

  return (
    <div>

      <h1 className="text-2xl font-bold mb-4">Dataset Viewer</h1>

      <div className="bg-white p-4 rounded shadow overflow-x-auto">

        <table className="w-full border">

          <thead>
            <tr>
              {data.columns.map((c) => (
                <th key={c} className="border p-2 bg-gray-100">
                  {c}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.data.map((row, i) => (
              <tr key={i}>
                {data.columns.map((c) => (
                  <td key={c} className="border p-2">
                    {row[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>

        </table>

      </div>

      {/* STATS */}
      {data.stats && (
        <pre className="mt-4 bg-gray-900 text-white p-4 rounded overflow-auto">
          {JSON.stringify(data.stats, null, 2)}
        </pre>
      )}

    </div>
  );
}
