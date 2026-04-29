from collections import deque


class MemoryManager:
    """
    Lightweight conversational memory
    Stores last N interactions
    """

    def __init__(self, max_history=5):
        self.history = deque(maxlen=max_history)
        self.last_plan = None

    # ----------------------------
    # Add interaction
    # ----------------------------
    def add(self, user_query: str, response: dict):
        self.history.append({
            "query": user_query,
            "response": response
        })

    # ----------------------------
    # Store last LLM plan
    # ----------------------------
    def set_last_plan(self, plan: dict):
        self.last_plan = plan

    def get_last_plan(self):
        return self.last_plan

    # ----------------------------
    # Get context for LLM
    # ----------------------------
    def get_context(self):
        context = []

        for item in self.history:
            response = item.get("response", {})
            response_type = response.get("type")
            response_preview = ""

            if response_type == "text":
                response_preview = str(response.get("content", ""))[:240]
            elif response_type in {"analysis", "table", "prediction", "chart"}:
                response_preview = response_type

            context.append({
                "query": item["query"],
                "response_type": response_type,
                "response_preview": response_preview,
            })

        return context

    # ----------------------------
    # Clear memory
    # ----------------------------
    def clear(self):
        self.history.clear()
        self.last_plan = None
