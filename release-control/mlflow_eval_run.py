import os

import mlflow

# Run this after eval_prompts.py prints eval_score=...
mlflow.set_experiment("afyaplus-triage")
with mlflow.start_run(run_name=os.getenv("GITHUB_SHA", "local")[:7]):
    mlflow.log_param("model", os.getenv("LLM_MODEL", "gpt-4o-mini"))
    mlflow.log_param("prompt_version", os.getenv("PROMPT_VERSION", "1.2.0"))
    mlflow.log_param("temperature", os.getenv("TRIAGE_TEMPERATURE", "0.2"))
    mlflow.log_metric("eval_score", float(os.getenv("EVAL_SCORE", "0.0")))
    mlflow.log_metric("threshold", 0.85)
print("logged run")