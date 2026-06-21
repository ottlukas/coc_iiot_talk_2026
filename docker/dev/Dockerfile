FROM node:20-alpine

# Set node environment
ENV NODE_ENV=development

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install packages
RUN npm install

# Copy scripts
COPY scripts ./scripts/

# Install Chromium for Puppeteer and test tooling
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont

RUN npm install puppeteer jest

# Expose live-reload dev-server port
EXPOSE 4200

# Start watching and serving
CMD ["node", "scripts/watch.js"]
