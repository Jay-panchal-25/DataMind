from services.llm_service import llm_service

SYSTEM_PROMPT = """
You are a senior data analyst.

Write a short, plain-English dataset summary.
Keep it concise, useful, and non-technical.
Mention the most important quality issues only if they matter.
Do not mention model errors or API failures.
"""


def summarize_insights(insights: dict):
    prompt = f"""
Dataset insights:
{insights}

Write a short summary in 3 to 5 lines.
"""

    text, error = llm_service.invoke_text(SYSTEM_PROMPT, prompt, temperature=0.2)
    if text:
        return text

    return _fallback_summary(insights, error)


def _fallback_summary(insights: dict, error: str | None):
    summary = insights.get("summary", {})
    missing = insights.get("missing", {})
    correlation = insights.get("correlation", [])

    parts = [
        f"Dataset has {summary.get('rows', 0)} rows and {summary.get('columns', 0)} columns."
    ]

    if missing:
        parts.append(
            f"Missing values were detected in {len(missing)} column(s)."
        )

    if correlation:
        pair = correlation[0]
        parts.append(
            f"Strong correlation found between {pair.get('feature_1')} and {pair.get('feature_2')}."
        )

    return " ".join(parts)
