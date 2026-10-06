# Secrets hygiene evidence
- [ ] .env is in .gitignore
- [ ] git check-ignore -v .env prints a rule
- [ ] git log --all -- .env is empty, or you rotated after a leak
- [ ] Compose files reference ${JWT_SECRET} and do not inline the value