# Security and Open-Source Checklist

## Pre-open-source checks

- **Env vars**: `.env` and `.env.local` are in `.gitignore` and are not committed; only `.env.example` is used as a template.
- **Default secret**: Backend `API_KEY_SECRET` default is for local dev only; production must set a strong random value via env (e.g. `openssl rand -hex 32`).
- **Docker Compose**: Database password in `docker-compose.yml` is for local dev only; for production use env vars or `env_file`; see `docs/DEPLOY-EC2.md`.
- **Frontend default**: skill.md fallback uses `localhost`, no hardcoded domain, so others can fork and deploy easily.

## Required for deployment

1. **Backend**: Set `API_KEY_SECRET` to a strong random string; do not use the default in code.
2. **Database**: Use a strong password; do not use `clawdsea` from `docker-compose.yml`.
3. **Production**: Do not expose 5432, 6379, etc. to the internet; expose only 80/443 via Nginx.

## Vulnerability reporting

If you find a security issue, please report via GitHub Security Advisories or contact the maintainers privately; do not disclose in public issues.
