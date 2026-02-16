export default function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-4xl ${
          isUser ? "bg-neutral-600 text-white" : "bg-gray-800 text-gray-200"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
