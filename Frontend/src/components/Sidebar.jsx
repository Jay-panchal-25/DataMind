import FileUpload from "./FileUpload";
import { Link, useLocation } from "react-router-dom";
import { MessageSquare, Database } from "lucide-react";

export default function Sidebar() {
  const location = useLocation();

  const navItem = (path, label, Icon) => (
    <Link
      to={path}
      className={`flex items-center gap-3 px-3 py-2 rounded-lg transition
        ${
          location.pathname === path
            ? "bg-neutral-800 text-white"
            : "text-neutral-400 hover:bg-neutral-800"
        }`}
    >
      <Icon size={18} />
      {label}
    </Link>
  );

  return (
    <div className="w-64 h-screen bg-neutral-950 border-r border-neutral-800 flex flex-col">
      <div className="border-b border-neutral-800 flex justify-center">
        <img src="/logo.png" alt="DataMind Logo" className="w-40 h-40" />
      </div>

      <div className="px-2 space-y-2 mt-4">
        {navItem("/", "Chat", MessageSquare)}
        {navItem("/dataset", "Dataset Viewer", Database)}
      </div>

      <div className="mt-auto p-3 border-t border-neutral-800">
        <FileUpload />
      </div>
    </div>
  );
}
