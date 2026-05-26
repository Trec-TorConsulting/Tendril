FROM --platform=$BUILDPLATFORM 192.168.4.10:30500/mirror/node:26-slim AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_URL=https://api.tendrilgrow.com/v1
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NODE_OPTIONS="--max-old-space-size=4096"
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM 192.168.4.10:30500/mirror/node:26-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN npm cache clean --force && rm -rf /usr/local/lib/node_modules/npm
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
