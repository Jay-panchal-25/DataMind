import { useState, useRef, useEffect } from "react";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! How can I help you?" },
  ]);

  // reference to bottom div for auto scroll
  const bottomRef = useRef(null);

  // auto scroll when new message added
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages]);

  // send message function
  const sendMessage = (text) => {
    if (!text || !text.trim()) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text,
      },
      {
        role: "assistant",
        content: "This is a mock AI response.",
      },
    ]);
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
        <ChatInput onSend={sendMessage} />
      </div>
    </div>
  );
}
