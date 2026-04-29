import json

from services.gemini_helper import generate_text

SYSTEM_PROMPT = """
You are an AI data analyst inside a dataset chat product.

Given a user question, an execution plan, and the computed result,
write a concise answer that directly addresses the question.

Rules:
- Be accurate and grounded only in the provided result
- Use plain English
- Keep it short
- If a grouped table is returned, summarize the main takeaway in 1 to 3 lines
- Do not mention internal planning, code, or tools
"""


def synthesize_answer(query: str, plan: dict, result: dict):
    preview = {
        "type": result.get("type"),
        "columns": result.get("columns", []),
        "rows": (result.get("rows") or [])[:8],
        "content": result.get("content"),
    }

    prompt = f"""
User question:
{query}

Execution plan:
{json.dumps(plan, ensure_ascii=False)}

Computed result:
{json.dumps(preview, ensure_ascii=False)}

Write the final answer.
"""

    text, _ = generate_text(SYSTEM_PROMPT, prompt, temperature=0.15)
    if text:
        return text

    return _fallback_answer(query, preview)


def _fallback_answer(query: str, preview: dict):
    result_type = preview.get("type")

    if result_type == "table":
        rows = preview.get("rows") or []
        columns = preview.get("columns") or []

        if rows and any(column.endswith("_max") or column.endswith("_min") for column in columns):
            summaries = []
            label_column = columns[0] if columns else None

            for row in rows[:5]:
                label = row.get(label_column) if label_column else None
                metrics = []
                for column in columns[1:]:
                    metrics.append(f"{column.replace('_', ' ')} {row.get(column)}")

                if label:
                    summaries.append(f"{label}: {', '.join(metrics)}")
                else:
                    summaries.append(", ".join(metrics))

            return "Grouped result: " + "; ".join(summaries) + "."

        if len(rows) == 1:
            first_row = rows[0]
            values = ", ".join(f"{key}: {value}" for key, value in first_row.items())
            return f"Here is the matching result for '{query}': {values}."

        if rows:
            first_row = rows[0]
            preview_values = ", ".join(
                f"{key}: {value}" for key, value in list(first_row.items())[:4]
            )
            return (
                f"I found {len(rows)} result rows for '{query}'. "
                f"The first result is {preview_values}."
            )

        return f"I found results for '{query}'."

    if preview.get("content"):
        return str(preview["content"])

    return "Here is the result."
