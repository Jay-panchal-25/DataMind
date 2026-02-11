from core.pipeline_manager import run_pipeline

result = run_pipeline("Backend/Testing dataset/messy_dataset.csv")

print(result["data"].head(20))
