# One AfyaPlus triage request, three numbers, three owners
latency_p95_ms = 1800          # product / SLO owner
throughput_rps = 12            # platform / capacity owner
cost_per_1k_usd = 0.42         # FinOps / CTO slide

# Never report only one. A "faster" model that triples $/1k fails the partnership brief.
print(latency_p95_ms, throughput_rps, cost_per_1k_usd)