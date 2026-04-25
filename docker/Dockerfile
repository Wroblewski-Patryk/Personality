FROM node:22-bookworm-slim AS web-build

ARG APP_BUILD_REVISION=unknown

WORKDIR /app/web

COPY web/package.json web/package-lock.json /app/web/
RUN npm ci
COPY web /app/web
ENV VITE_APP_BUILD_REVISION=${APP_BUILD_REVISION}
RUN npm run build

FROM python:3.11-slim

ARG APP_BUILD_REVISION=unknown

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_BUILD_REVISION=${APP_BUILD_REVISION}

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/README.md /app/backend/
COPY backend/app /app/backend/app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -e /app/backend

COPY backend /app/backend
COPY docker /app/docker
COPY --from=web-build /app/web/dist /app/web/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
