FROM ruby:3.2-slim

ENV LANG C.UTF-8

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    nodejs \
    npm \
    inotify-tools \
    ca-certificates \
    git \
    nginx \
    wget \
  && rm -rf /var/lib/apt/lists/*

# Asciidoctor for AsciiDoc -> RevealJS (with CDN support for reveal.js)
RUN gem install asciidoctor-revealjs --no-document

# reveal-md for Markdown slides
RUN npm install -g reveal-md

# Remove default nginx config to avoid conflicts
RUN rm -f /etc/nginx/sites-enabled/default

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY watch-and-build.sh /usr/local/bin/watch-and-build.sh
RUN chmod +x /usr/local/bin/watch-and-build.sh

WORKDIR /src

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

ENTRYPOINT ["/usr/local/bin/watch-and-build.sh"]
