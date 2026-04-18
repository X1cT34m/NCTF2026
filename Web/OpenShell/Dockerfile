FROM node:24-bookworm-slim AS opencode

RUN npm install -g --no-fund --no-audit opencode-ai@1.2.16 && \
    cp /usr/local/lib/node_modules/opencode-ai/bin/.opencode /opencode && \
    chmod 755 /opencode

FROM node:24-bookworm-slim

ENV NODE_ENV=production

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium-headless-shell && \
    rm -rf /var/lib/apt/lists/*

COPY --from=opencode /opencode /usr/local/bin/opencode

WORKDIR /app/

COPY ./app/package.json /app/package.json

RUN npm install --omit=dev --no-fund --no-audit && \
    npm cache clean --force

COPY --chown=node:node ./app/ /app/
COPY --chmod=755 ./entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
