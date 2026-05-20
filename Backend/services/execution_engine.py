import pandas as pd

from services.json_utils import to_json_safe


def _apply_filter(data: pd.DataFrame, column: str, operator: str, value):
    if operator == "==":
        return data[data[column] == value]
    if operator == "!=":
        return data[data[column] != value]
    if operator == ">":
        return data[data[column] > value]
    if operator == ">=":
        return data[data[column] >= value]
    if operator == "<":
        return data[data[column] < value]
    if operator == "<=":
        return data[data[column] <= value]
    raise ValueError(f"Unsupported operator '{operator}'")


def execute_analysis(df: pd.DataFrame, plan: dict):

    if not isinstance(plan, dict) or "steps" not in plan:
        return {"error": "Invalid execution plan"}

    data = df.copy()
    groupby_cols = []

    try:
        for step in plan["steps"]:
            action = step.get("action")

            # ---------------- FILTER ----------------
            if action == "filter":
                col = step.get("column")
                op = step.get("operator")
                val = step.get("value")

                if col not in data.columns:
                    return {"error": f"Column '{col}' not found"}

                data = _apply_filter(data, col, op, val)

            # ---------------- DROPNA ----------------
            elif action == "dropna":
                cols = step.get("columns")

                if not cols:
                    return {"error": "dropna requires 'columns'"}

                for col in cols:
                    if col not in data.columns:
                        return {"error": f"Column '{col}' not found"}

                data = data.dropna(subset=cols)

            # ---------------- FILLNA ----------------
            elif action == "fillna":
                col = step.get("column")
                method = step.get("method", "mean")

                if col not in data.columns:
                    return {"error": f"Column '{col}' not found"}

                if method == "mean":
                    fill_value = data[col].mean()
                elif method == "median":
                    fill_value = data[col].median()
                else:
                    return {"error": f"Unsupported fillna method '{method}'"}

                data[col] = data[col].fillna(fill_value)

            # ---------------- GROUPBY ----------------
            elif action == "groupby":
                groupby_cols = step.get("columns", [])

                if not groupby_cols:
                    return {"error": "groupby requires 'columns'"}

                for col in groupby_cols:
                    if col not in data.columns:
                        return {"error": f"Column '{col}' not found"}

            # ---------------- SELECT ----------------
            elif action == "select":
                cols = step.get("columns") or []
                if not cols:
                    return {"error": "select requires 'columns'"}

                for col in cols:
                    if col not in data.columns:
                        return {"error": f"Column '{col}' not found"}

                data = data.loc[:, cols]

            # ---------------- AGGREGATE ----------------
            elif action == "aggregate":
                agg_ops = step.get("operations")

                if not agg_ops:
                    return {"error": "aggregate requires 'operations'"}

                # Validate columns
                for col in agg_ops.keys():
                    if col not in data.columns:
                        return {"error": f"Column '{col}' not found"}

                if groupby_cols:
                    result = data.groupby(groupby_cols).agg(agg_ops)
                else:
                    result = data.agg(agg_ops)

                data = _normalize_aggregate_result(result, groupby_cols, agg_ops)

            # ---------------- SORT ----------------
            elif action == "sort":
                col = step.get("column")
                order = step.get("order", "asc")

                if col not in data.columns:
                    return {"error": f"Column '{col}' not found"}

                data = data.sort_values(
                    by=col,
                    ascending=(order == "asc")
                )

            # ---------------- LIMIT ----------------
            elif action == "limit":
                limit_val = step.get("value", 5)
                data = data.head(limit_val)

        # ---------------- FINAL OUTPUT ----------------

        if data.empty:
            return {
                "type": "text",
                "content": "No data found after applying conditions."
            }

        if _is_single_value_result(data, plan):
            column_name = data.columns[0]
            value = data.iloc[0, 0]
            operations = plan.get("operations") or []
            operation = ", ".join(operations) if operations else plan.get("operation", "result")

            return {
                "type": "text",
                "content": f"{operation.capitalize()} {column_name}: {value}"
            }

        return {
            "type": "table",
            "columns": data.columns.tolist(),
            "rows": to_json_safe(data.to_dict(orient="records"))
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def _normalize_aggregate_result(result, groupby_cols, agg_ops):
    if isinstance(result, pd.DataFrame):
        normalized = result.copy()

        if isinstance(normalized.columns, pd.MultiIndex):
            normalized.columns = [
                f"{col}_{func}" for col, func in normalized.columns
            ]

        if groupby_cols:
            return normalized.reset_index()

        if not normalized.index.equals(pd.RangeIndex(len(normalized))):
            normalized = normalized.reset_index(drop=True)

        return normalized

    if isinstance(result, pd.Series):
        if groupby_cols:
            normalized = result.reset_index()
            normalized.columns = [
                *groupby_cols,
                _single_agg_label(agg_ops)
            ]
            return normalized

        return pd.DataFrame([result.to_dict()])

    return pd.DataFrame([{"result": result}])


def _single_agg_label(agg_ops):
    if not agg_ops:
        return "value"

    keys = list(agg_ops.keys())
    return keys[0] if len(keys) == 1 else "value"


def _is_single_value_result(data: pd.DataFrame, plan: dict):
    return (
        plan.get("operation") not in (None, "none")
        and not plan.get("groupby")
        and isinstance(data, pd.DataFrame)
        and len(data.index) == 1
        and len(data.columns) == 1
    )
