ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror
FROM --platform=$BUILDPLATFORM ${BASE_REGISTRY}/node:26-slim AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=https://api.tendrilgrow.com/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NODE_OPTIONS="--max-old-space-size=4096"
COPY package.json package-lock.json ./
# --legacy-peer-deps needed for openapi-typescript@7 (peer-warns on TS 6
# but output is pure .d.ts text and works fine). See PR #189.
RUN npm ci --legacy-peer-deps
COPY . .
RUN npm run build

ARG BASE_REGISTRY=registry.registry.svc.cluster.local:5000/mirror
FROM ${BASE_REGISTRY}/node:26-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN npm cache clean --force && rm -rf /usr/local/lib/node_modules/npm
# node:26-slim ships an unprivileged 'node' user (uid 1000), matching the
# k8s securityContext runAsUser.
COPY --from=builder --chown=node:node /app/public ./public
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
USER node
EXPOSE 3000
# Container-level liveness for docker/compose runtimes. Kubernetes uses its
# own readiness/liveness probes.
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/',r=>process.exit(r.statusCode<500?0:1)).on('error',()=>process.exit(1))"
CMD ["node", "server.js"]
