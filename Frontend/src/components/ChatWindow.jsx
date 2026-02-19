import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: "assistant", type: "text", content: "Hello! How can I help you?" },
  ]);

  const [isSending, setIsSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text || !text.trim()) return;

    // Add user message
    setMessages((prev) => [
      ...prev,
      { role: "user", type: "text", content: text },
    ]);

    setIsSending(true);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error("Request failed");
      }

      const data = await res.json();

      // DO NOT convert to text
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: data.type,
          content: data.content,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "text",
          content: "Unable to reach backend. Please ensure the API is running.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-neutral-900 overflow-hidden">
      <div className="flex-1 overflow-y-auto no-scrollbar px-25 py-6 space-y-6">
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            role={msg.role}
            type={msg.type}
            content={msg.content}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="bg-neutral-900 px-20">
        <ChatInput onSend={sendMessage} disabled={isSending} />
      </div>
    </div>
  );
}
