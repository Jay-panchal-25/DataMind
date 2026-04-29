import { useState } from "react";
import axios from "axios";

import ChatMessage from "../components/ChatMessage";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      type: "user",
      content: input,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: input,
      });

      const botMessage = {
        type: res.data.type,
        content: res.data.content,
      };

      setMessages([...updatedMessages, botMessage]);

    } catch {
      setMessages([
        ...updatedMessages,
        {
          type: "text",
          content: "Error: Failed to get response from server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">

      {/* HEADER */}
      <div className="p-4 bg-white border-b font-bold text-lg">
        DataMind Chat
      </div>

      {/* CHAT AREA */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">

        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}

        {loading && (
          <div className="text-gray-500 text-sm">
            Thinking...
          </div>
        )}

      </div>

      {/* INPUT AREA */}
      <div className="p-3 bg-white border-t flex gap-2">

        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask your dataset..."
          className="flex-1 border rounded px-3 py-2"
        />

        <button
          onClick={sendMessage}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Send
        </button>

      </div>

    </div>
  );
}
