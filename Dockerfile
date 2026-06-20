FROM node:20-alpine

# Set node environment
ENV NODE_ENV=development

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install packages
RUN npm install

# Copy compile and watch scripts
COPY compile.js watch.js ./

# Expose live-reload dev-server port
EXPOSE 4200

# Start watching and serving
CMD ["node", "watch.js"]
