import FileUpload from "./FileUpload";
import { Link, useLocation } from "react-router-dom";
import { MessageSquare, Database, BarChart3 } from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  const navItem = (path, label, Icon) => (
    <Link
      to={path}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm font-semibold
        ${
          location.pathname === path
            ? "bg-white text-neutral-900 shadow-sm"
            : "text-neutral-300 hover:bg-neutral-800/80"
        }`}
    >
      <Icon size={18} />
      {label}
    </Link>
  );

  return (
    <div className="w-72 h-screen bg-neutral-900 border-r border-neutral-800 flex flex-col shadow-xl shadow-black/20">
      <div className="border-b border-neutral-800 px-6 py-6">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="DataMind Logo" className="w-12 h-12 rounded-xl ring-1 ring-neutral-700" />
          <div>
            <p className="text-xl font-extrabold text-neutral-100 tracking-tight">DataMind</p>
            <p className="text-xs text-neutral-400">Data Chat Workspace</p>
          </div>
        </div>
      </div>

      <div className="px-4 space-y-2 mt-5">
        {navItem("/", "Chat", MessageSquare)}
        {navItem("/dataset", "Dataset Viewer", Database)}
        {navItem("/graph", "AI Graph", BarChart3)}
      </div>

      <div className="mt-auto p-4 border-t border-neutral-800 bg-neutral-900">
        <FileUpload />
      </div>
    </div>
  );
}

