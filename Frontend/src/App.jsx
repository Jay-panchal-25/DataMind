import { useEffect, useRef, useState } from "react";

import ChatMessage from "./components/ChatMessage";
import Sidebar from "./components/Sidebar";
import { getDataset, sendChat, uploadFile } from "./services/app";

const PAGE_SIZE = 12;

export default function App() {
  const [file, setFile] = useState(null);
  const [datasetMeta, setDatasetMeta] = useState(null);
  const [datasetPage, setDatasetPage] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [activeView, setActiveView] = useState("dataset");
  const [stage, setStage] = useState("upload");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function loadDatasetPage(nextPage = 1) {
    try {
      const response = await getDataset(nextPage, PAGE_SIZE);
      setDatasetPage(response.data);
    } catch (err) {
      setError(
        err?.response?.data?.detail || "Unable to load dataset preview."
      );
    }
  }

  async function handleUpload() {
    if (!file) {
      setError("Select a dataset first.");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const response = await uploadFile(file);
      const payload = response.data;

      if (payload.error) {
        setError(payload.error);
        return;
      }

      setDatasetMeta({
        ...payload,
        fileName: file.name,
      });
      setDatasetPage(null);
      setMessages([]);
      setInput("");
      setActiveView("dataset");
      setStage("overview");
      await loadDatasetPage(1);
    } catch (err) {
      setError(err?.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleSendMessage() {
    const trimmed = input.trim();

    if (!trimmed || !datasetMeta || loading) {
      return;
    }

    const nextMessages = [
      ...messages,
      {
        type: "user",
        content: trimmed,
      },
    ];

    setMessages(nextMessages);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const response = await sendChat(trimmed);
      setMessages([
        ...nextMessages,
        {
          type: response.data?.type ?? "text",
          content: response.data?.content ?? "No response returned.",
        },
      ]);
    } catch (err) {
      setMessages([
        ...nextMessages,
        {
          type: "text",
          content: err?.response?.data?.detail || "Request failed.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function openWorkspace(view) {
    setActiveView(view);
    setStage("workspace");
  }

  const hasDataset = Boolean(datasetMeta);

  return (
    <div className="min-h-screen bg-[#020402] text-[#e8ffe8]">
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.14),_transparent_30%),linear-gradient(180deg,_#040704_0%,_#010201_100%)]">
        <div className="mx-auto max-w-[1600px] p-4 lg:p-6">
          {error && (
            <div className="mb-4 rounded-2xl border border-[#3f1717] bg-[#140707] px-4 py-3 text-sm text-[#ffb4b4]">
              {error}
            </div>
          )}

          {stage === "upload" && (
            <UploadStage
              file={file}
              onFileChange={setFile}
              onUpload={handleUpload}
              uploading={uploading}
            />
          )}

          {stage === "overview" && hasDataset && (
            <OverviewStage
              datasetMeta={datasetMeta}
              onOpenChat={() => openWorkspace("chat")}
              onOpenDataset={() => openWorkspace("dataset")}
            />
          )}

          {stage === "workspace" && hasDataset && (
            <div className="flex min-h-[calc(100vh-3rem)] flex-col gap-4 lg:flex-row">
              <Sidebar
                activeView={activeView}
                datasetMeta={datasetMeta}
                onViewChange={setActiveView}
              />

              <main className="flex min-h-[calc(100vh-3rem)] flex-1 overflow-hidden rounded-[28px] border border-[#17301d] bg-[#050805] shadow-[0_24px_90px_rgba(0,0,0,0.55)]">
                {activeView === "dataset" ? (
                  <DatasetWorkspace
                    data={datasetPage}
                    onPageChange={loadDatasetPage}
                  />
                ) : (
                  <ChatWorkspace
                    chatEndRef={chatEndRef}
                    datasetMeta={datasetMeta}
                    input={input}
                    loading={loading}
                    messages={messages}
                    onInputChange={setInput}
                    onSend={handleSendMessage}
                  />
                )}
              </main>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function UploadStage({ file, onFileChange, onUpload, uploading }) {
  return (
    <div className="flex min-h-[calc(100vh-3rem)] items-center justify-center">
      <div className="w-full max-w-2xl rounded-[32px] border border-[#17301d] bg-[#071007] p-8 shadow-[0_24px_90px_rgba(0,0,0,0.45)]">
        <p className="text-xs uppercase tracking-[0.34em] text-[#74c184]">
          welcome to DataMind
        </p>
        <h1 className="mt-4 text-4xl font-semibold text-white">
          Upload your dataset
        </h1>
        <p className="mt-3 text-sm leading-7 text-[#83a287]">
          Start with a file. After upload, you’ll review the dataset details and
          then enter the analysis workspace.
        </p>

        <label className="mt-8 flex cursor-pointer flex-col items-center justify-center rounded-[28px] border border-dashed border-[#285532] bg-[#030603] px-6 py-16 text-center transition hover:border-[#3f8f4d]">
          <span className="text-lg font-medium text-white">
            {file ? file.name : "Choose CSV, Excel, or JSON"}
          </span>
          <span className="mt-2 text-sm text-[#7b977f]">
            Click to select a file
          </span>
          <input
            type="file"
            className="hidden"
            accept=".csv,.xlsx,.xls,.json"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
        </label>

        <button
          type="button"
          onClick={onUpload}
          disabled={uploading}
          className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-[#1faa59] px-4 py-3 text-sm font-semibold text-[#021603] transition hover:bg-[#23c865] disabled:cursor-not-allowed disabled:bg-[#16351f] disabled:text-[#71927a]"
        >
          {uploading ? "Uploading..." : "Upload dataset"}
        </button>
      </div>
    </div>
  );
}

function OverviewStage({ datasetMeta, onOpenChat, onOpenDataset }) {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-3rem)] max-w-5xl items-center">
      <div className="w-full rounded-[32px] border border-[#17301d] bg-[#071007] p-8 shadow-[0_24px_90px_rgba(0,0,0,0.45)]">
        <p className="text-sm text-[#8ab38f]">Upload successful</p>
        <h1 className="mt-2 text-3xl font-semibold text-white">
          {datasetMeta.fileName}
        </h1>
        <p className="mt-4 text-sm leading-7 text-[#89a78d]">
          {datasetMeta.summary}
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <section className="rounded-[24px] border border-[#17301d] bg-[#050a05] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-[#74c184]">
              Dataset info
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <InfoTile label="Rows" value={datasetMeta.report?.overview?.rows ?? 0} />
              <InfoTile
                label="Columns"
                value={datasetMeta.report?.overview?.columns ?? 0}
              />
              <InfoTile
                label="File size"
                value={`${datasetMeta.report?.overview?.file_size_mb ?? 0} MB`}
              />
              <InfoTile
                label="Memory"
                value={`${datasetMeta.report?.overview?.memory_usage_mb ?? 0} MB`}
              />
            </div>
          </section>

          <section className="rounded-[24px] border border-[#17301d] bg-[#050a05] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-[#74c184]">
              What was fixed
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <InfoTile
                label="Duplicates removed"
                value={datasetMeta.report?.fixes?.duplicates_removed ?? 0}
              />
              <InfoTile
                label="Missing filled"
                value={datasetMeta.report?.fixes?.missing_filled ?? 0}
              />
              <InfoTile
                label="Missing remaining"
                value={datasetMeta.report?.fixes?.missing_after ?? 0}
              />
              <InfoTile
                label="Outliers corrected"
                value={datasetMeta.report?.fixes?.outlier_updates ?? 0}
              />
            </div>
          </section>
        </div>

    

        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={onOpenDataset}
            className="inline-flex items-center justify-center rounded-2xl border border-[#2b7a3f] bg-[#0c190e] px-5 py-3 text-sm font-semibold text-[#dfffe5] transition hover:bg-[#102313]"
          >
            View dataset
          </button>
          <button
            type="button"
            onClick={onOpenChat}
            className="inline-flex items-center justify-center rounded-2xl bg-[#1faa59] px-5 py-3 text-sm font-semibold text-[#021603] transition hover:bg-[#23c865]"
          >
            Let&apos;s start analysis
          </button>
        </div>
      </div>
    </div>
  );
}

function DatasetWorkspace({ data, onPageChange }) {
  if (!data) {
    return (
      <div className="flex-1 p-6">
        <div className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5 text-sm text-[#8ab38f]">
          Loading dataset...
        </div>
      </div>
    );
  }

  const report = data.report ?? {};

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mx-auto max-w-7xl space-y-5">
        <div className="rounded-[28px] border border-[#17301d] bg-[#071007] p-6">
          <p className="text-xs uppercase tracking-[0.3em] text-[#74c184]">
            Dataset viewer
          </p>
          <h1 className="mt-3 text-3xl font-semibold text-white">
            Full dataset and details
          </h1>
          <p className="mt-3 text-sm text-[#86a58a]">
            Explore the cleaned dataset, review fixes, and inspect the preview
            table from one page.
          </p>
        </div>

        <div className="grid gap-4 xl:grid-cols-2">
          <section className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-[#74c184]">
              Dataset info
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <InfoTile label="Rows" value={report.overview?.rows ?? 0} />
              <InfoTile label="Columns" value={report.overview?.columns ?? 0} />
              <InfoTile
                label="File size"
                value={`${report.overview?.file_size_mb ?? 0} MB`}
              />
              <InfoTile
                label="Memory"
                value={`${report.overview?.memory_usage_mb ?? 0} MB`}
              />
            </div>
          </section>

          <section className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5">
            <p className="text-xs uppercase tracking-[0.24em] text-[#74c184]">
              What was fixed
            </p>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <InfoTile
                label="Duplicates removed"
                value={report.fixes?.duplicates_removed ?? 0}
              />
              <InfoTile
                label="Missing filled"
                value={report.fixes?.missing_filled ?? 0}
              />
              <InfoTile
                label="Missing remaining"
                value={report.fixes?.missing_after ?? 0}
              />
              <InfoTile
                label="Outliers corrected"
                value={report.fixes?.outlier_updates ?? 0}
              />
            </div>
          </section>
        </div>


        <section className="rounded-[24px] border border-[#17301d] bg-[#071007] p-5">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-[#8ab38f]">
              Page {data.page} of {data.total_pages}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => onPageChange(Math.max(1, data.page - 1))}
                disabled={data.page <= 1}
                className="rounded-xl border border-[#1a3920] bg-[#081008] px-3 py-2 text-sm text-[#d6f7dc] transition hover:bg-[#0d180d] disabled:cursor-not-allowed disabled:text-[#527059]"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => onPageChange(Math.min(data.total_pages, data.page + 1))}
                disabled={data.page >= data.total_pages}
                className="rounded-xl border border-[#1a3920] bg-[#081008] px-3 py-2 text-sm text-[#d6f7dc] transition hover:bg-[#0d180d] disabled:cursor-not-allowed disabled:text-[#527059]"
              >
                Next
              </button>
            </div>
          </div>

          <div className="mt-5 overflow-hidden rounded-[20px] border border-[#17301d]">
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-[#0c150c] text-[#dfffe5]">
                  <tr>
                    {data.columns.map((column) => (
                      <th
                        key={column}
                        className="border-b border-[#17301d] px-4 py-3"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.data.map((row, rowIndex) => (
                    <tr
                      key={rowIndex}
                      className="border-b border-[#112015] odd:bg-[#060b06] even:bg-[#040804]"
                    >
                      {data.columns.map((column) => (
                        <td
                          key={`${rowIndex}-${column}`}
                          className="max-w-[240px] px-4 py-3 text-[#d2ecd6]"
                        >
                          <span className="block overflow-hidden break-words">
                            {formatCellValue(row[column])}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function ChatWorkspace({
  chatEndRef,
  datasetMeta,
  input,
  loading,
  messages,
  onInputChange,
  onSend,
}) {
  return (
    <div className="flex min-h-0 min-h-[calc(100vh-3rem)] flex-1 flex-col">
      <div className="border-b border-[#112015] px-6 py-5">
        <p className="text-xs uppercase tracking-[0.3em] text-[#74c184]">
          Analysis chat
        </p>
        <h1 className="mt-3 text-2xl font-semibold text-white">
          Chat with your dataset
        </h1>
        <p className="mt-2 text-sm text-[#86a58a]">
          Ask questions, request charts, grouped metrics, filters, or
          predictions.
        </p>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 && !loading ? (
          <div className="mx-auto max-w-4xl rounded-[28px] border border-[#17301d] bg-[#071007] px-6 py-7">
            <p className="text-sm text-[#8ab38f]">Ready to analyze</p>
            <h2 className="mt-2 text-2xl font-semibold text-white">
              Start asking about {datasetMeta.fileName}
            </h2>
          </div>
        ) : (
          <div className="mx-auto w-full max-w-4xl space-y-4">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}

            {loading && (
              <div className="inline-flex items-center gap-2 rounded-full border border-[#1f4b28] bg-[#091409] px-4 py-2 text-sm text-[#95c79d]">
                <span className="h-2 w-2 animate-pulse rounded-full bg-[#2bd96b]" />
                Thinking...
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        )}
      </div>

      <div className="shrink-0 border-t border-[#112015] px-6 py-5">
        <div className="mx-auto max-w-4xl">
          <div className="flex gap-3 rounded-[24px] border border-[#17301d] bg-[#050905] p-3">
            <textarea
              value={input}
              onChange={(event) => onInputChange(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  onSend();
                }
              }}
              rows={2}
              disabled={loading}
              placeholder="Ask about your dataset..."
              className="min-h-[78px] flex-1 resize-none rounded-[20px] border border-[#17301d] bg-[#071007] px-4 py-3 text-sm text-white outline-none placeholder:text-[#67816b] focus:border-[#2fa44e] disabled:cursor-not-allowed disabled:text-[#67816b]"
            />

            <button
              type="button"
              onClick={onSend}
              disabled={loading || !input.trim()}
              className="inline-flex h-[52px] items-center justify-center self-end rounded-[18px] bg-[#1faa59] px-5 text-sm font-semibold text-[#021603] transition hover:bg-[#23c865] disabled:cursor-not-allowed disabled:bg-[#16351f] disabled:text-[#71927a]"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function SuggestionPill({ label }) {
  return (
    <span className="rounded-full border border-[#1f4b28] bg-[#091409] px-4 py-2 text-sm text-[#cfead4]">
      {label}
    </span>
  );
}

function InfoTile({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#17301d] bg-[#050a05] px-4 py-3">
      <p className="text-xs uppercase tracking-[0.22em] text-[#6f9576]">{label}</p>
      <p className="mt-2 text-base font-medium text-white">{value}</p>
    </div>
  );
}

function formatCellValue(value) {
  if (value === null || value === undefined || value === "") {
    return "Unknown";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}
