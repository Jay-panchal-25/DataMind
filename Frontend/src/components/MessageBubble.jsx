import ChartRenderer from "./ChartRenderer";

export default function MessageBubble({ role, type, content }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`rounded-2xl px-4 py-3 max-w-[70%] ${
          isUser ? "bg-blue-600 text-white" : "bg-neutral-800 text-white"
        }`}
      >
        {type === "chart" ? (
          <ChartRenderer chart={content} />
        ) : (
          <p>{content}</p>
        )}
      </div>
    </div>
  );
}
