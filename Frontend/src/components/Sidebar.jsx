import FileUpload from "./FileUpload";
import { MessageSquare, LineChart, Plus } from "lucide-react";

export default function Sidebar({ mode, setMode }) {
  return (
    <div className="w-64 h-screen bg-neutral-950 border-r border-neutral-800 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-neutral-800">
        <h1 className="text-white font-semibold text-lg">DataMind AI</h1>
      </div>

      {/* New Chat */}
      <div className="p-3">
        <button className="w-full flex items-center gap-2 px-3 py-2 bg-neutral-800 hover:bg-neutral-700 text-white rounded-lg">
          <Plus size={16} />
          New Chat
        </button>
      </div>

      {/* Modes (LIKE GEMINI) */}
      <div className="px-2 space-y-1">
        {/* Chat */}
        <div
          onClick={() => setMode("chat")}
          className={`
            flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer
            ${
              mode === "chat"
                ? "bg-neutral-800 text-white"
                : "text-neutral-400 hover:bg-neutral-800"
            }
          `}
        >
          <MessageSquare size={18} />
          Chat
        </div>

        {/* Generate Graph */}
        <div
          onClick={() => setMode("graph")}
          className={`
            flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer
            ${
              mode === "graph"
                ? "bg-neutral-800 text-white"
                : "text-neutral-400 hover:bg-neutral-800"
            }
          `}
        >
          <LineChart size={18} />
          Generate Graph
        </div>
      </div>

      {/* Upload at bottom */}
      <div className="mt-auto p-3 border-t border-neutral-800">
        <FileUpload />
      </div>
    </div>
  );
}
