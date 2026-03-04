import ChartRenderer from "./ChartRenderer";
import DataTable from "./DataTable";

export default function MessageBubble({ role, type, content }) {
  const isUser = role === "user";
  const isTable = type === "table";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`rounded-2xl px-4 py-3 shadow-sm ${isTable ? "max-w-[84%]" : "max-w-[70%]"} ${
          isUser
            ? "bg-neutral-700 text-white"
            : "bg-neutral-900 text-neutral-100 border border-neutral-700"
        }`}
      >
        {type === "chart" ? (
          <ChartRenderer chart={content} />
        ) : type === "table" ? (
          <DataTable table={content} />
        ) : (
          <p className="leading-relaxed text-sm">{content}</p>
        )}
      </div>
    </div>
  );
}
