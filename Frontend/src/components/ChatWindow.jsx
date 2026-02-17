import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! How can I help you?" },
  ]);
  const [isSending, setIsSending] = useState(false);

  // reference to bottom div for auto scroll
  const bottomRef = useRef(null);

  // auto scroll when new message added
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  const formatBackendReply = (payload) => {
    if (!payload || typeof payload !== "object") {
      return "Invalid response from server.";
    }

    if (payload.type === "text") {
      return String(payload.content ?? "");
    }

    if (payload.type === "chart") {
      if (typeof payload.content === "string") {
        return payload.content;
      }

      const file = payload.content?.file ?? "";
      const chartType = payload.content?.chart_type ?? "chart";
      const column = payload.content?.column ?? "column";
      return `Generated ${chartType} for ${column}: ${file}`;
    }

    return "I received a response in an unknown format.";
  };

  // send message function
  const sendMessage = async (text) => {
    if (!text || !text.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
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

      let responseText = "";

      if (!res.ok) {
        responseText = `Request failed (${res.status})`;
      } else {
        const data = await res.json();
        responseText = formatBackendReply(data);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: responseText,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Unable to reach backend. Please ensure the API is running.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-neutral-900 overflow-hidden">
      {/* Messages container */}
      <div className="flex-1 overflow-y-auto no-scrollbar px-25 py-6 space-y-6">
        {messages.map((msg, index) => (
          <MessageBubble key={index} role={msg.role} content={msg.content} />
        ))}

        {/* auto scroll anchor */}
        <div ref={bottomRef} />
      </div>

      {/* Input container */}
      <div className=" bg-neutral-900 px-20 ">
        <ChatInput onSend={sendMessage} disabled={isSending} />
      </div>
    </div>
  );
}
