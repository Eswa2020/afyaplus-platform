# AfyaPlus Service Platform — Engineering Report

Sep 26, 2026 · @Esther Kamau

## 1. Platform overview

The AfyaPlus Service Platform is a three-layer AI service architecture built end to end this week, using the health-logistics scenario as the concrete domain.

**Layer 1 — Secure API** (`secure_triage_api.py`): a FastAPI service wrapping a triage model behind JWT authentication. Typed Pydantic request/response models enforce input constraints; a `/token` login endpoint issues signed, expiring tokens; protected routes verify the token and the caller's role before running; `/health` stays open for monitoring probes. Rate limiting and role-based permissions (403 vs 401) are layered on top.

**Layer 2 — Containerisation**: the same service is frozen into a Docker image (`afyaplus-triage:1.0.0`, 247MB disk usage, 59.1MB unique content), built from a slim Python base with dependency layers ordered before code for fast rebuilds. Secrets are injected only at container start via `--env-file`, never baked into the image — verified directly by inspecting a container's environment and filesystem. The image tag matches a corresponding Git tag (`v1.0.0`).

**Layer 3 — MCP Agent**: a logistics MCP server (`logistics_mcp.py`) exposes three tools (`check_stock`, `plan_delivery_route`, `get_delivery_eta`) and one resource (the clinic directory), each with input validation, errors returned as instructive data, and per-call logging. A LangChain agent (`gpt-4o-mini`) consumes these tools through the MCP protocol, exposed via its own authenticated FastAPI endpoint (`agent_api.py`) that reuses the same JWT auth module as Layer 1. The agent is additionally wrapped in three safety rails: role-based permissions, a human-in-the-loop proposal/confirm flow for actions that change real data, and idempotency protection against retried requests.

Every layer traces back to the same underlying discipline: validate at the door, fail honestly with the correct status code, and never let a caller's mistake or a dependency's failure become an unexplained crash.

## 2. Version control evidence

The repository (`afyaplus-platform`) is a Git repository from its first commit, with a `.gitignore` committed before any secret file existed, and a tagged release (`v1.0.0`) matching the Docker image tag.

A merge conflict was deliberately induced and resolved to demonstrate the team's conflict-resolution habit: a feature branch (`feature/rename-title`) and `master` each changed the same line in `secure_triage_api.py` (the FastAPI service title) differently. Merging produced a real conflict:

```
CONFLICT (content): Merge conflict in secure_triage_api.py
Automatic merge failed; fix conflicts and then commit the result.
```

Resolution followed the three-step procedure documented in `CONTRIBUTING.md`: the conflicting `<<<<<<<` / `=======` / `>>>>>>>` markers were read, one version of the line was kept and the markers removed, the resolution was committed (`git commit -m "Resolve title merge conflict"`), and — critically — the service was restarted and its `/health` endpoint verified before considering the conflict closed. This last step confirmed the resolution did not silently break the running service.

Branching and versioning policy (branch naming, maximum branch age, semantic version meaning, and the release-tagging procedure) is documented in `CONTRIBUTING.md` at the root of the repository.

## 3. Containerisation evidence

The triage service builds into a single Docker image from a `python:3.12-slim` base, with a Dockerfile ordered so dependency installation (`COPY requirements.txt` + `pip install`) is cached separately from application code (`COPY auth.py secure_triage_api.py rate_limit.py`). A rebuild after only a code change completed in 5.3 seconds (all dependency layers served from cache), versus 77.5 seconds for a cold build — direct evidence the layer ordering works as intended.

**Image identity:**

| Property | Value |
| --- | --- |
| Image tag | `afyaplus-triage:1.0.0` |
| Matching Git tag | `v1.0.0` |
| Disk usage | 247 MB |
| Unique content size | 59.1 MB |
| Base image | `python:3.12-slim` |

Secrets are never present in the image itself. This was verified directly: starting a fresh container *without* `--env-file` and inspecting its environment (`env | grep JWT_SECRET`) returned nothing, and listing the container's files (`ls -la`) showed only the four files explicitly copied by the Dockerfile (`auth.py`, `rate_limit.py`, `requirements.txt`, `secure_triage_api.py`) — no `.env` present. Secrets are injected only at container start via `--env-file .env`, confirmed by the service correctly authenticating requests only when started that way.

## 4. Observability: reconstructing a request from its trace

Every request to `/ask-logistics` is assigned a short trace id at the door, logged at request end with timing, question length (never the question text itself, to avoid storing potentially sensitive content), and token/cost usage.

**Example trace, pulled directly from `agent_api.log`:**

```
trace=1f766134 user=mercy ms=10909 question_chars=34
trace=3f4f5e51 user=mercy ms=10881 question_chars=30 tokens_in=652 tokens_out=117 model_calls=2
```

From this single log line alone, a support engineer can reconstruct: who asked (`mercy`), how long the request took end-to-end (10.9 seconds), roughly how complex the question was (30–34 characters), and — once cost logging was added — exactly how expensive it was (652 input tokens, 117 output tokens, across 2 model-call iterations of the agent loop). The trace id (`3f4f5e51`) is the same identifier returned to the caller in the API response, so a user reporting a problem can quote it back, collapsing what would otherwise be a cross-log manual investigation into a single `grep` against `agent_api.log`.

This proved its worth beyond the happy path during testing: a cross-server composition test (logistics + a second docs policy server) produced an agent response that quietly failed to call the expected `get_policy` tool, instead generating plausible but ungrounded text. Because every request is traced, that specific failing request's cost and timing were immediately isolable in the log for follow-up, even though the failure itself was a model tool-selection issue rather than a service error — demonstrating that the trace infrastructure is valuable for diagnosing behavioural failures, not only outages.

## 5. Stakeholder memo

**To:** AfyaPlus leadership **From:** Engineering **Re:** Logistics & triage platform pilot readiness

**What was built.** A three-layer platform: a secured, containerised triage API; an MCP server exposing stock-lookup, route-planning, and delivery-time-estimate tools grounded in real clinic data; and an LLM agent that consumes those tools to answer Mercy's logistics questions in plain language, all behind the same authentication system, with every request traceable end to end.

**Highest-value component.** The agent-plus-MCP layer is where the platform actually changes how work gets done: it replaces Mercy acting as a human API between a spreadsheet and everyone who needs an answer, turning multi-hour phone-call-and-spreadsheet cycles into sub-30-second answers grounded in real tool data. The other layers (auth, containers, tracing) are what make that agent *safe and operable*, not what make it valuable on their own — but none of them are optional: without JWT there is no defensible partner-facing rollout, and without traces a wrong recommendation cannot be explained after the fact.

**One risk, with mitigation.** Testing surfaced a concrete failure mode: when given tools from two independent MCP servers, the agent did not reliably select the correct tool for a policy-lookup question, instead generating plausible but ungrounded text rather than calling the real `get_policy` tool — even though that tool worked correctly in isolation. This is a tool-selection reliability risk, not a security or infrastructure risk. Mitigation: sharpen tool docstrings to more closely match the phrasing real users are likely to use (the same fix that resolved an earlier hallucinated-pricing failure during testing), and, before any production rollout, expand the honest-failure testing already used for pricing questions to cover every tool boundary, not just the ones exercised so far.

**Recommendation: Go, with conditions.** The core architecture (auth, containerisation, tool validation, tracing) is production-grade and evidenced end to end. Conditions before a partner-facing rollout: (1) HTTPS in front of the JWT token exchange, since tokens are currently only proven safe over plain HTTP in a local testing context; (2) the tool-selection reliability risk above resolved and re-tested across all published tools, not only the ones that surfaced the issue; (3) the in-memory rate limiter and session store replaced with a shared store (e.g. Redis) before running more than one service copy, since both currently reset per-process rather than being shared across copies.
