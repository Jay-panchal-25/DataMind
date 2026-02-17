import { useState } from "react";
import {
  Upload,
  FileText,
  Loader2,
  CheckCircle,
  RefreshCw,
} from "lucide-react";

export default function FileUpload() {
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");
  const [uploaded, setUploaded] = useState(false);

  const uploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);
    setLoading(true);
    setStatus("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setStatus(data.message);
      setUploaded(true); // hide upload input
    } catch {
      setStatus("Upload failed");
      setUploaded(false);
    }

    setLoading(false);
  };

  const resetUpload = () => {
    setUploaded(false);
    setFileName("");
    setStatus("");
  };

  return (
    <div className="p-4 border-b border-neutral-800">
      {/* SHOW UPLOAD BOX ONLY IF NOT UPLOADED */}
      {!uploaded && (
        <label className="cursor-pointer block">
          <input
            type="file"
            accept=".csv"
            onChange={uploadFile}
            className="hidden"
          />

          <div className="flex flex-col items-center justify-center gap-2 p-4 border border-dashed border-neutral-700 rounded-xl hover:border-neutral-500 transition-all bg-neutral-900">
            {loading ? (
              <>
                <Loader2 className="animate-spin text-neutral-400" size={22} />
                <p className="text-sm text-neutral-400">Uploading...</p>
              </>
            ) : (
              <>
                <Upload size={22} className="text-neutral-400" />
                <p className="text-sm text-neutral-300 font-medium">
                  Upload CSV Dataset
                </p>
                <p className="text-xs text-neutral-500">Click to select file</p>
              </>
            )}
          </div>
        </label>
      )}

      {/* SHOW SUCCESS STATE */}
      {uploaded && (
        <div className="flex items-center justify-between p-3 bg-neutral-900 border border-neutral-800 rounded-xl">
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle size={16} />
            <div>
              <p className="text-xs font-medium text-white">Dataset Ready</p>
              <p className="text-xs text-neutral-400">{fileName}</p>
            </div>
          </div>

          {/* Replace button */}
          <button
            onClick={resetUpload}
            className="text-neutral-400 hover:text-white"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      )}

      {/* Status */}
      {status && !uploaded && (
        <p className="text-xs mt-2 text-green-400">{status}</p>
      )}
    </div>
  );
}
