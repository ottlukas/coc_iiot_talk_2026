#!/bin/sh
set -e

SRC_DIR=/src
OUT_DIR=/usr/share/nginx/html

mkdir -p "$OUT_DIR"

# Copy assets to output first
if [ -d "$SRC_DIR/assets" ]; then
  echo "[$(date '+%H:%M:%S')] Copying assets..."
  mkdir -p "$OUT_DIR/assets"
  cp -r "$SRC_DIR/assets"/* "$OUT_DIR/assets/" 2>/dev/null || true
fi

# Copy images to output
if [ -d "$SRC_DIR/images" ]; then
  echo "[$(date '+%H:%M:%S')] Copying images..."
  mkdir -p "$OUT_DIR/images"
  cp -r "$SRC_DIR/images"/* "$OUT_DIR/images/" 2>/dev/null || true
fi

# Build AsciiDoc slides with full reveal.js path
echo "[$(date '+%H:%M:%S')] Building slides.adoc with asciidoctor-revealjs..."
if [ -f "$SRC_DIR/slides.adoc" ]; then
  asciidoctor-revealjs \
    -a revealjs_theme=solarized \
    -a revealjs_cdnjs_version=4.5.0 \
    -a revealjs_hash=true \
    -a revealjs_slideNumber=true \
    -o "$OUT_DIR/index.html" \
    "$SRC_DIR/slides.adoc" 2>&1 || echo "[$(date '+%H:%M:%S')] Warning: asciidoctor-revealjs had issues"
    # Normalize reveal.js asset paths so they point to the static /reveal location
    if [ -f "$OUT_DIR/index.html" ]; then
      sed -i 's|href="reveal.js/dist/|href="/reveal/dist/|g' "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i "s|src=\"./dist/reveal.js\"|src=\"/reveal/dist/reveal.js\"|g" "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i 's|src="./plugin/|src="/reveal/plugin/|g' "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i 's|href="./dist/reveal.css"|href="/reveal/dist/reveal.css"|g' "$OUT_DIR/index.html" 2>/dev/null || true
    fi
fi

# Build Reveal markdown variant as fallback/alternative
echo "[$(date '+%H:%M:%S')] Building reveal-full.md with reveal-md..."
if command -v reveal-md >/dev/null 2>&1; then
  if [ -f "$SRC_DIR/reveal-full.md" ]; then
    mkdir -p "$OUT_DIR/reveal"
    reveal-md "$SRC_DIR/reveal-full.md" \
      --static "$OUT_DIR/reveal" \
      --highlight-theme monokai \
      2>&1 || echo "[$(date '+%H:%M:%S')] Warning: reveal-md had issues"
    # copy assets to reveal folder
    if [ -d "$OUT_DIR/assets" ]; then
      cp -r "$OUT_DIR/assets" "$OUT_DIR/reveal/" 2>/dev/null || true
    fi
    # Ensure reveal.js assets are also available at /reveal.js for Asciidoctor output
    if [ -d "$OUT_DIR/reveal/dist" ]; then
      mkdir -p "$OUT_DIR/reveal.js"
      cp -r "$OUT_DIR/reveal/dist" "$OUT_DIR/reveal.js/" 2>/dev/null || true
    fi
    if [ -d "$OUT_DIR/reveal/plugin" ]; then
      mkdir -p "$OUT_DIR/reveal.js"
      cp -r "$OUT_DIR/reveal/plugin" "$OUT_DIR/reveal.js/" 2>/dev/null || true
    fi
  fi
fi

# Create fallback index.html if primary build failed
if [ ! -f "$OUT_DIR/index.html" ] || [ ! -s "$OUT_DIR/index.html" ]; then
  echo "[$(date '+%H:%M:%S')] Creating fallback index.html..."
  cat > "$OUT_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Open Source for Regulated Manufacturing</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/solarized.css">
  <link rel="stylesheet" href="assets/reveal-theme.css">
  <style>
    body { margin: 0; overflow: hidden; background: #fafafa; }
    .reveal { width: 100%; height: 100vh; }
    .reveal-content { padding: 40px; text-align: center; }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section class="reveal-content">
        <h1>Open Source for Regulated Manufacturing</h1>
        <h3>GMP‑Compliant IIoT Data Logging with Apache IoTDB</h3>
        <p style="margin-top: 40px; color: #666;"><em>Lukas Ott — CommunityOverCode 2026</em></p>
      </section>
      <section class="reveal-content">
        <h2>The 2026 Regulatory Storm</h2>
        <ul style="text-align: left;">
          <li><strong>Annex 11 Overhaul:</strong> ~1,500 → ~10,000 words</li>
          <li><strong>Annex 22:</strong> AI-supported systems in GMP</li>
          <li><strong>The Collision:</strong> High-frequency IIoT meets strictest compliance</li>
        </ul>
      </section>
      <section class="reveal-content">
        <h2>Compliance in 60 Seconds</h2>
        <div style="display: flex; gap: 20px; text-align: left;">
          <div style="flex: 1;"><h3>🇺🇸 FDA — 21 CFR Part 11</h3><ul style="font-size: 0.8em;"><li>Electronic records & signatures</li><li>Secure validation</li><li>Audit trails</li></ul></div>
          <div style="flex: 1;"><h3>🇪🇺 EU — Annex 11</h3><ul style="font-size: 0.8em;"><li>Lifecycle validation</li><li>ALCOA+ data integrity</li><li>Cloud & AI controls</li></ul></div>
        </div>
      </section>
      <section class="reveal-content">
        <h2>Apache IoTDB as GMP Historian</h2>
        <ul style="text-align: left;">
          <li>⚡ High-throughput time-series ingestion</li>
          <li>🔐 Access controls & encryption</li>
          <li>🗃️ TSFile immutable storage</li>
          <li>🔁 Integrates with Iceberg for cold storage</li>
        </ul>
      </section>
      <section class="reveal-content">
        <h2>Key Takeaways</h2>
        <ol style="text-align: left;">
          <li>Open Source enables verifiable validation</li>
          <li>IoTDB + TSFile + Iceberg = ALCOA++ architecture</li>
          <li>Break vendor lock-in with ASF technologies</li>
        </ol>
      </section>
      <section class="reveal-content">
        <h2>Questions?</h2>
        <p><strong>Lukas Ott</strong> — Enterprise Architect</p>
        <p><a href="https://iotdb.apache.org/" target="_blank">https://iotdb.apache.org/</a></p>
      </section>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/plugin/notes/notes.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/plugin/highlight/highlight.js"></script>
  <script src="assets/interactive.js"></script>
  <script>
    Reveal.initialize({
      hash: true,
      slideNumber: true,
      transition: 'slide',
      plugins: [ RevealNotes, RevealHighlight ]
    });
  </script>
</body>
</html>
EOF
  echo "✓ Fallback index.html created"
fi

echo ""
echo "[$(date '+%H:%M:%S')] Build complete! Files in $OUT_DIR:"
ls -lah "$OUT_DIR/" 2>/dev/null | head -20
echo ""

# Start nginx in background
echo "[$(date '+%H:%M:%S')] Starting nginx..."
nginx -g 'daemon off;' &
NGINX_PID=$!

# Watch for changes
echo "[$(date '+%H:%M:%S')] Watching $SRC_DIR for changes..."
while true; do
  inotifywait -e modify,create,delete -r "$SRC_DIR" >/dev/null 2>&1 || true
  echo "[$(date '+%H:%M:%S')] Change detected, rebuilding..."
  
  # Rebuild
  if [ -f "$SRC_DIR/slides.adoc" ]; then
    asciidoctor-revealjs \
      -a revealjs_theme=solarized \
      -a revealjs_cdnjs_version=4.5.0 \
      -o "$OUT_DIR/index.html" \
      "$SRC_DIR/slides.adoc" 2>&1 || true
    # Normalize reveal.js asset paths in rebuilt index.html
    if [ -f "$OUT_DIR/index.html" ]; then
      sed -i 's|href="reveal.js/dist/|href="/reveal/dist/|g' "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i "s|src=\"./dist/reveal.js\"|src=\"/reveal/dist/reveal.js\"|g" "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i 's|src="./plugin/|src="/reveal/plugin/|g' "$OUT_DIR/index.html" 2>/dev/null || true
      sed -i 's|href="./dist/reveal.css"|href="/reveal/dist/reveal.css"|g' "$OUT_DIR/index.html" 2>/dev/null || true
    fi
  fi
  
  if command -v reveal-md >/dev/null 2>&1 && [ -f "$SRC_DIR/reveal-full.md" ]; then
    mkdir -p "$OUT_DIR/reveal"
    reveal-md "$SRC_DIR/reveal-full.md" --static "$OUT_DIR/reveal" 2>&1 || true
    # Mirror reveal-md static assets to /reveal.js so Asciidoctor-generated HTML can find reveal.js
    if [ -d "$OUT_DIR/reveal/dist" ]; then
      mkdir -p "$OUT_DIR/reveal.js"
      cp -r "$OUT_DIR/reveal/dist" "$OUT_DIR/reveal.js/" 2>/dev/null || true
    fi
    if [ -d "$OUT_DIR/reveal/plugin" ]; then
      mkdir -p "$OUT_DIR/reveal.js"
      cp -r "$OUT_DIR/reveal/plugin" "$OUT_DIR/reveal.js/" 2>/dev/null || true
    fi
  fi
  
  # Copy any changed assets
  if [ -d "$SRC_DIR/assets" ]; then
    cp -r "$SRC_DIR/assets"/* "$OUT_DIR/assets/" 2>/dev/null || true
  fi
  
  echo "[$(date '+%H:%M:%S')] Rebuild complete"
done
