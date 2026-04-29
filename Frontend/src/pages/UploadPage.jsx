import { useState } from "react";
import { uploadFile } from "../services/app";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);

  const handleUpload = async () => {
    const res = await uploadFile(file);
    setData(res.data);
  };

  return (
    <div className="max-w-3xl mx-auto">

      <h1 className="text-3xl font-bold mb-6">Upload Dataset</h1>

      <div className="bg-white p-6 rounded-xl shadow">

        <input
          type="file"
          className="mb-4"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button
          onClick={handleUpload}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Upload
        </button>

      </div>

      {/* STATS */}
      {data && (
        <div className="grid grid-cols-3 gap-4 mt-6">

          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500">Rows</h2>
            <p className="text-xl font-bold">{data.rows}</p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500">Columns</h2>
            <p className="text-xl font-bold">{data.columns.length}</p>
          </div>

          <div className="bg-white p-4 rounded shadow">
            <h2 className="text-gray-500">Status</h2>
            <p className="text-green-600 font-bold">Ready</p>
          </div>

        </div>
      )}

      {/* SUMMARY */}
      {data?.summary && (
        <div className="bg-white mt-6 p-4 rounded shadow">
          <h2 className="font-bold mb-2">AI Summary</h2>
          <p>{data.summary}</p>
        </div>
      )}

    </div>
  );
}