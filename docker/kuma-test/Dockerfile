# Throwaway Uptime Kuma server for the integration tests. Built from source at a
# pinned commit; we deliberately do not use the upstream images or Dockerfile.
# Not for production: no healthcheck, no rootless variant, tests wipe all data.
#
#   docker build -t kuma-test --build-arg KUMA_REF=<sha> docker/kuma-test
#   docker run --rm -p 3001:3001 kuma-test
#
# Pinned values live in docker/kuma-test/versions.env (KUMA_VERSION -> KUMA_REF).
ARG NODE_IMAGE=node:24-bookworm-slim@sha256:a5f4366e834695d5f363b920c104953a535d3a9864d1bdf74566a0ebe01daee5

FROM ${NODE_IMAGE} AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates python3 make g++ \
 && rm -rf /var/lib/apt/lists/*
ARG KUMA_REF
RUN test -n "$KUMA_REF" || (echo "KUMA_REF (full commit sha) is required" && false)
WORKDIR /app
RUN git init -q . \
 && git remote add origin https://github.com/louislam/uptime-kuma.git \
 && git fetch -q --depth 1 origin "$KUMA_REF" \
 && git checkout -q FETCH_HEAD \
 && test "$(git rev-parse HEAD)" = "$KUMA_REF" \
 && rm -rf .git
RUN npm ci --no-audit --no-fund \
 && npm run build \
 && npm prune --omit=dev

FROM ${NODE_IMAGE}
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates iputils-ping \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build --chown=node:node /app /app
RUN mkdir -p /app/data && chown node:node /app/data
USER node
ENV NODE_ENV=production UPTIME_KUMA_PORT=3001 UPTIME_KUMA_DB_TYPE=sqlite
EXPOSE 3001
VOLUME /app/data
CMD ["node", "server/server.js"]
