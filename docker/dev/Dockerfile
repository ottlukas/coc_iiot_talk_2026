FROM node:20-slim

# Set node environment
ENV NODE_ENV=development

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install packages
RUN npm install

# Copy scripts
COPY scripts ./scripts/

# Install Chromium and emoji font support for Puppeteer PDF export
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-noto-color-emoji \
    fontconfig \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install puppeteer jest

# Expose live-reload dev-server port
EXPOSE 4200

# Start watching and serving
CMD ["node", "scripts/watch.js"]
