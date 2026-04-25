# AION / Personality

This repository follows the approved `v2` product topology:

- `backend/` for the Python runtime, API, memory, workers, tests, and scripts
- `web/` for the browser client workspace
- `mobile/` for the mobile client workspace
- `docs/` for canonical architecture, engineering, planning, and ops truth

The current production runtime still lives entirely in `backend/`. `web/` and
`mobile/` are the next product layers that will consume stable backend-facing
contracts.

## Quick Start

1. Copy the root env template:

```bash
cp .env.example .env
```

2. Start the local stack:

```bash
docker compose up --build
```

3. Start the browser client when working on the product shell:

```bash
cd web
npm install
npm run dev
```

4. Check health:

```bash
curl http://localhost:8000/health
```

## Working Areas

- backend runtime and developer workflow:
  [backend/README.md](/C:/Personal/Projekty/Aplikacje/Personality/backend/README.md)
- canonical docs index:
  [docs/README.md](/C:/Personal/Projekty/Aplikacje/Personality/docs/README.md)

## Deployment

- local Docker uses [docker-compose.yml](/C:/Personal/Projekty/Aplikacje/Personality/docker-compose.yml)
- Coolify uses [docker-compose.coolify.yml](/C:/Personal/Projekty/Aplikacje/Personality/docker-compose.coolify.yml)
- the runtime image is built from [docker/Dockerfile](/C:/Personal/Projekty/Aplikacje/Personality/docker/Dockerfile)
