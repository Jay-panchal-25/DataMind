from core.pipeline_manager import run_pipeline

from ml.query_engine import QueryEngine

result = run_pipeline("Backend/Testing dataset/messy.csv")

engine = QueryEngine(result["data"])

query = input("Enter your query: ")

result = engine.execute(query)

print(result)


