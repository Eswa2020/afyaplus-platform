# Defense in depth
1. TLS (transit_policy.py)
2. Secrets hygiene (gitignore / vault refs)
3. AuthN with JWT, AuthZ with RBAC
4. injection_guard and allowlists
5. corpus pins
6. redacted logs and retention

One layer failing must not equal total compromise.