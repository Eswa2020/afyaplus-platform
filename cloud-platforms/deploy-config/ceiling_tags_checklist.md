# Ceiling & Tags Checklist

## Who owns this bill?
Owner **wanjiru**, cost-center **clinical-ai**, service **triage-api**, version **1.1.0**, env **staging**.
All five are labels on the triage-api service in `docker-compose.cost.yml`, and are
verified on the running container with `docker inspect`.

## What is the replica ceiling?
**4 replicas maximum.** Declared in two places that must agree:
- `docker-compose.cost.yml`: label `afyaplus.max-replicas: "4"`
- `serverless-ish.yaml`: `interactive.max_instances: 4`

Locally the service runs as 1 replica, because a fixed host port (8000) allows only one
container. In the cloud, the ceiling is enforced by the platform autoscaler
(Azure Container Apps max replicas, AWS ECS service auto-scaling max capacity, or a K8s HPA
`maxReplicas`), not by Compose. Without it, a retry storm becomes an unbounded bill.

## Cloud mapping
| Compose label | Azure tag key | AWS cost allocation tag |
|---|---|---|
| afyaplus.service | service | user:service |
| afyaplus.version | version | user:version |
| afyaplus.env | env | user:env |
| afyaplus.cost-center | cost-center | user:cost-center |
| afyaplus.owner | owner | user:owner |

On AWS, `user:` tags must also be activated as cost allocation tags in the Billing console
before they appear in Cost Explorer or can filter a budget.

## Soft budget link
The Lab 2 budgets filter on the `service = triage-api` tag (Azure `tags.service`,
AWS `user:service$triage-api`). If that tag is not applied to the cloud resources at
creation time, the budget still exists but its filter matches nothing, and the 80% alert
stops meaning anything about triage.