import { useState } from "react";

export default function ChatInput({ onSend, disabled = false }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (disabled) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="rounded-2xl border border-neutral-700 bg-neutral-900/95 shadow-2xl shadow-black/40">
      <div className="flex items-center rounded-2xl px-4 py-3">
        <input
          type="text"
          className="flex-1 bg-transparent outline-none text-neutral-100 placeholder:text-neutral-400 rounded-2xl text-sm"
          placeholder="Send a message..."
          value={input}
          disabled={disabled}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !disabled && handleSend()}
        />
        <button
          onClick={handleSend}
          disabled={disabled}
          className="ml-3 bg-white hover:bg-neutral-200 px-4 py-2 rounded-xl text-neutral-900 text-sm font-semibold disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {disabled ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

