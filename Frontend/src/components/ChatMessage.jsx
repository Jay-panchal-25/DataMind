import ChartRenderer from "./ChartRenderer";
import PredictionCard from "./PredictionCard";

export default function ChatMessage({ message }) {
  if (!message) return null;

  const { type, content } = message;

  if (type === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-[22px] rounded-br-md border border-[#2b7a3f] bg-[#1faa59] px-4 py-3 text-sm font-medium text-[#031504] shadow-[0_10px_25px_rgba(31,170,89,0.2)]">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[92%] space-y-3">
        {type === "text" && (
          <div className="rounded-[22px] rounded-bl-md border border-[#17301d] bg-[#081108] px-4 py-3 text-sm leading-7 text-[#e8ffe8]">
            {content}
          </div>
        )}

        {type === "analysis" && (
          <div className="space-y-3">

            {content.columns?.length > 0 && (
              <div className="overflow-hidden rounded-[22px] border border-[#17301d] bg-[#071007]">
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="bg-[#0c150c] text-[#e8ffe8]">
                      <tr>
                        {content.columns.map((column, index) => (
                          <th key={index} className="px-4 py-3 font-medium">
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {content.rows.map((row, rowIndex) => (
                        <tr
                          key={rowIndex}
                          className="border-t border-[#17301d] text-[#d7f0db] odd:bg-[#060b06]"
                        >
                          {content.columns.map((column, columnIndex) => (
                            <td key={columnIndex} className="px-4 py-3 align-top">
                              {String(row[column])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {type === "table" && (
          <div className="overflow-hidden rounded-[22px] border border-[#17301d] bg-[#071007]">
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-[#0c150c] text-[#e8ffe8]">
                  <tr>
                    {content.columns.map((column, index) => (
                      <th key={index} className="px-4 py-3 font-medium">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {content.rows.map((row, rowIndex) => (
                    <tr
                      key={rowIndex}
                      className="border-t border-[#17301d] text-[#d7f0db] odd:bg-[#060b06]"
                    >
                      {content.columns.map((column, columnIndex) => (
                        <td key={columnIndex} className="px-4 py-3 align-top">
                          {String(row[column])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {type === "chart" && <ChartRenderer data={content} />}

        {type === "prediction" && <PredictionCard data={content} />}
      </div>
    </div>
  );
}
