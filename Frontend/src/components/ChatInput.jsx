import { useState } from "react";

export default function ChatInput({ onSend }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    onSend(input);
    setInput("");
  };

  return (
    <div className="border-t border-gray-800 mb-7 rounded-4xl  bg-neutral-800">
      <div className="flex items-center bg-neutral-800 rounded-4xl px-4 py-2">
        <input
          type="text"
          className="flex-1 bg-transparent outline-none text-white rounded-4xl"
          placeholder="Send a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <button
          onClick={handleSend}
          className="ml-3 bg-white hover:bg-gray-400 px-4 py-1 rounded-4xl text-black"
        >
          Send
        </button>
      </div>
    </div>
  );
}
