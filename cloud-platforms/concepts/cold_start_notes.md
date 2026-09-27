Measure: time from invoke → first /health 200 after idle.
Mitigations: min instances, provisioned concurrency, smaller images (multi-stage builds),
keep LLM client init lazy if the model call is rare on that path.