# Endpoint Switch Drill

Same image (`triage-api:1.1.0`, image ID `sha256:e7afe62ca5a8...`),
same `docker-compose.cost.yml`, no code change and no rebuild between runs.
The provider is chosen only by the `LLM_BASE_URL` and `LLM_MODEL` environment variables.

## Run A, local / mock (default)
LLM_BASE_URL=http://127.0.0.1:8088/v1
LLM_MODEL=gpt-4o-mini

`docker compose -f docker-compose.cost.yml config`:
    LLM_BASE_URL: http://127.0.0.1:8088/v1
    LLM_MODEL: gpt-4o-mini

Running service, `GET /health`:
    {"service":"triage-api","version":"1.1.0","status":"ok","llm_base_url":"http://127.0.0.1:8088/v1","llm_model":"gpt-4o-mini"}

## Run B, Nebius-shaped
LLM_BASE_URL=https://api.studio.nebius.ai/v1
LLM_MODEL=meta-llama/Meta-Llama-3.1-8B-Instruct

`docker compose -f docker-compose.cost.yml config`:
    LLM_BASE_URL: https://api.studio.nebius.ai/v1
    LLM_MODEL: meta-llama/Meta-Llama-3.1-8B-Instruct

Running service, `GET /health`:
    {"service":"triage-api","version":"1.1.0","status":"ok","llm_base_url":"https://api.studio.nebius.ai/v1","llm_model":"meta-llama/Meta-Llama-3.1-8B-Instruct"}

## What this proves
- The switch is configuration, not a code fork: Compose recreated the container with new
  settings, and the running app reported them.
- The triage model is still a stub, so no request reached either provider and no key was used.
  A live Nebius call would also need a real `LLM_API_KEY` injected at runtime, never baked into the image.

## Bedrock note
Bedrock is not OpenAI-wire-compatible by default: it typically uses the AWS SDK with IAM
credentials and a different request shape, so switching to it needs a thin adapter behind the
same triage client interface, not just a new `LLM_BASE_URL`.