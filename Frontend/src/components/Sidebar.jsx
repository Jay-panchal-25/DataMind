export default function Sidebar({ activeView, datasetMeta, onViewChange }) {
  return (
    <aside className="w-full shrink-0 rounded-[28px] border border-[#17301d] bg-[#050905] p-5 lg:w-[290px]">
      <p className="text-xs uppercase tracking-[0.3em] text-[#74c184]">
        DataMind
      </p>
      <h2 className="mt-3 text-3xl font-semibold text-white">Workspace</h2>

      <div className="mt-8 space-y-3">
        <SidebarButton
          active={activeView === "dataset"}
          label="Dataset viewer"
          onClick={() => onViewChange("dataset")}
        />

        <SidebarButton
          active={activeView === "chat"}
          label="Chat section"
          onClick={() => onViewChange("chat")}
        />
      </div>

      <div className="mt-8 rounded-[24px] border border-[#17301d] bg-[#071007] p-4">
        <p className="text-xs uppercase tracking-[0.24em] text-[#74c184]">
          Current dataset
        </p>
        <p className="mt-3 break-words text-sm font-medium text-white">
          {datasetMeta.fileName}
        </p>
        <div className="mt-4 space-y-3 text-sm text-[#b8dfbf]">
          <SidebarLine label="Rows" value={datasetMeta.rows} />
          <SidebarLine label="Columns" value={datasetMeta.columns.length} />
          <SidebarLine label="Status" value="Ready" />
        </div>
      </div>
    </aside>
  );
}

function SidebarButton({ active, label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-[20px] border px-4 py-3 text-left text-sm font-medium transition ${
        active
          ? "border-[#2b7a3f] bg-[#0d1b0f] text-[#dfffe5]"
          : "border-[#17301d] bg-[#071007] text-[#b8dfbf] hover:bg-[#0a140b]"
      }`}
    >
      {label}
    </button>
  );
}

function SidebarLine({ label, value }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-[#7fa486]">{label}</span>
      <span className="text-white">{value}</span>
    </div>
  );
}
