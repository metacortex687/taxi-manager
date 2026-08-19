FROM mcr.microsoft.com/playwright:v1.61.0-noble

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY export-png.mjs ./

ENTRYPOINT ["node", "/app/export-png.mjs"]
