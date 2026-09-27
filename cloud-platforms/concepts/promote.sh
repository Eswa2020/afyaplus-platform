# Build once, push to a registry, pull in any cloud
docker tag triage-api:1.0.0 ghcr.io/afyaplus/triage-api:1.0.0
docker push ghcr.io/afyaplus/triage-api:1.0.0
# Azure / AWS / Nebius then reference:
# image: ghcr.io/afyaplus/triage-api:1.0.0
# with region, IAM pull rights, and env for LLM_BASE_URL