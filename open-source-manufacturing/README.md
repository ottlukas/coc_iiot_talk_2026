# Open Source for Regulated Manufacturing

A RevealJS presentation on building scalable, auditable, and compliant IIoT data platforms with Apache Software Foundation (ASF) technologies. Prepared for Apache Community Over Code 2026.

## Contents

- `slides.adoc` — AsciiDoc slides rendered with RevealJS (11 slides)
- `reveal-full.md` — Markdown variant with interactive elements (Chart.js regulatory chart, clickable pipeline)
- `assets/reveal-theme.css` — Custom teal/blue theme with animations
- `assets/interactive.js` — Pipeline step handlers and fragment animations
- `images/` — Diagrams and supporting images
- `Dockerfile` — Unified build + server environment (Ruby + Node.js + nginx)
- `nginx.conf` — Web server configuration with caching and compression

## Quick Start (Docker)

### Build & Run

```bash
# Navigate to the project directory
cd open-source-manufacturing

# Build the Docker image
docker compose build

# Start the container (builds slides and serves on port 8080)
docker compose up
```

Then open **http://localhost:8080** in your browser.

### Access the Presentation

- **AsciiDoc variant (default):** http://localhost:8080/
- **Markdown variant:** http://localhost:8080/reveal/

**Note:** Both variants are compiled from the same source and feature custom theming, animations, and interactivity.

### Hot Reload & Auto-Rebuild

The container watches for changes in:
- `slides.adoc` — Triggers AsciiDoc rebuild  
- `reveal-full.md` — Triggers Markdown rebuild
- `assets/` — Copied to output on change
- `images/` — Copied to output on change

**Workflow:**
1. Edit any source file (e.g., `slides.adoc`)
2. Save the file (the container detects the change automatically)
3. Refresh your browser (F5) to see the updated slides

No manual rebuild needed—the container's file watcher handles it.

## Local Build (Without Docker)

### Build AsciiDoc Slides

```bash
gem install asciidoctor-revealjs
asciidoctor-revealjs -a revealjs_theme=solarized slides.adoc -o slides.html
# Open slides.html in your browser
```

### Build Markdown Slides

```bash
npm install -g reveal-md
reveal-md reveal-full.md --static out/reveal
# Open out/reveal/index.html in your browser
```

### Live Preview (Python)

```bash
python -m http.server 8080
# Open http://localhost:8080
```

## Troubleshooting

### Issue: Blank page or 404 errors

**Solution:**
1. Check container logs:
   ```bash
   docker compose logs presentation
   ```
2. Verify files are being generated:
   ```bash
   docker compose exec presentation ls -lh /usr/share/nginx/html/
   ```
3. Test the server directly:
   ```bash
   curl -I http://localhost:8080/index.html
   ```
4. If the container exited, check why:
   ```bash
   docker compose logs presentation | tail -50
   ```

### Issue: CSS/JS not loading or appearing broken

**Solution:**
1. Hard refresh your browser to bypass cache:
   - **Windows/Linux:** `Ctrl+Shift+R`
   - **Mac:** `Cmd+Shift+R`
2. Open browser DevTools (F12) and check the **Network** tab for 404 errors
3. Verify assets were copied:
   ```bash
   docker compose exec presentation ls -lh /usr/share/nginx/html/assets/
   ```
4. If missing, rebuild:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

### Issue: Changes to slides not appearing

**Solution:**
1. The file watcher may not have detected the change. Verify in logs:
   ```bash
   docker compose logs -f presentation
   ```
2. Make sure you saved the file
3. Wait a few seconds for the rebuild to complete
4. Refresh the browser (F5)
5. If still not working, restart the container:
   ```bash
   docker compose restart
   ```

### Issue: Nginx config conflicts or duplicate server errors

**Solution:**
1. The Dockerfile automatically removes conflicting nginx default configs
2. If you still see nginx errors, rebuild without cache:
   ```bash
   docker compose build --no-cache
   docker compose up
   ```
3. Check nginx config syntax in container:
   ```bash
   docker compose exec presentation nginx -t
   ```

### Issue: Build tools not found (asciidoctor, reveal-md)

**Solution:**
1. A fallback HTML page is created if the build fails
2. Check the build output in logs for specific errors:
   ```bash
   docker compose logs presentation | grep -i error
   ```
3. Verify the Docker image contains the tools:
   ```bash
   docker compose exec presentation which asciidoctor-revealjs reveal-md
   ```

## Docker Compose Commands

```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs presentation

# Execute command in container
docker compose exec presentation sh

# Stop services
docker compose stop

# Remove containers and volumes
docker compose down

# Rebuild without cache
docker compose build --no-cache

# Rebuild and start
docker compose up --build
```

## Architecture

### Dockerfile (Unified Container)

The Dockerfile builds a single container that handles both **build** and **serve** responsibilities:

- **Base:** `ruby:3.2-slim` (includes Python, Git, build tools)
- **Node.js:** Installed for npm packages (reveal-md)
- **Build Tools:** 
  - `asciidoctor-revealjs` (gem) — Converts AsciiDoc → RevealJS HTML
  - `reveal-md` (npm) — Converts Markdown → RevealJS static site
- **Web Server:** `nginx` (Alpine stable) for serving files
- **File Watching:** `inotify-tools` for detecting source changes
- **Configuration:** Removes conflicting nginx default site, applies custom nginx.conf
- **Port:** 80 (mapped to 8080 on host via docker-compose)

### watch-and-build.sh (Build Script)

Entry point that orchestrates the build and serve workflow:

1. **Initialize directories** — Creates `/usr/share/nginx/html` output directory
2. **Copy assets** — Copies `assets/` and `images/` to nginx root
3. **Build AsciiDoc** — Runs `asciidoctor-revealjs` on `slides.adoc` → `index.html`
4. **Build Markdown** — Runs `reveal-md` on `reveal-full.md` → `/reveal/index.html` + assets
5. **Fallback HTML** — Creates basic index.html with CDN-based Reveal.js if builds fail
6. **Start nginx** — Launches nginx daemon in the background (`daemon off` mode)
7. **Watch loop** — Monitors `/src` for file changes, rebuilds on detection

**Key feature:** Runs continuously; nginx stays alive while watching for changes.

### nginx.conf (Web Server Config)

Serves static files with production-grade settings:

- **Root directory:** `/usr/share/nginx/html` (output from watch-and-build.sh)
- **SPA fallback:** `try_files $uri $uri/ /index.html` (supports Reveal.js routing)
- **MIME types:** Configured for HTML, CSS, JS, fonts, images
- **Caching:** 1-hour cache for `/assets/`, `/css/`, `/js/`, `/images/`
- **Compression:** gzip enabled for text, CSS, JavaScript
- **Security:** Headers for XSS protection, content-type sniffing prevention

### Interactive Elements

**assets/reveal-theme.css**
- Custom teal/blue color scheme (CSS variables: `--primary`, `--accent`, `--muted`)
- Responsive flexbox layouts for slides
- Fragment animations (fade-in, slide transitions)
- Component styles: cards, two-column layouts, pipeline steps, takeaway boxes

**assets/interactive.js**
- Event handlers for clickable pipeline step buttons (PLC4X, BifroMQ, Apache IoTDB, etc.)
- Shows/hides detailed descriptions for each component
- Reveal.js plugin integration for fragment visibility tracking
- DOMContentLoaded listener ensures handlers attach after page load

**reveal-full.md**
- 11 slides covering Apache IoTStack, regulatory expansion, and architecture
- Embedded Chart.js for regulatory chart visualization
- HTML snippets for interactive pipeline buttons
- Speaker notes for presenter context
- Fallback to `index.html` for directory requests

## Contributing

1. Edit `slides.adoc` for the primary slides
2. Edit `reveal-full.md` for the interactive variant
3. Modify `assets/reveal-theme.css` for styling
4. Add interactivity in `assets/interactive.js`
5. Add diagrams to `images/`
6. Update `module.yaml` metadata
7. Submit a pull request

## Notes

- Reveal.js library loaded from CDN (cdn.jsdelivr.net)
- Custom theme defines colors (teal/blue) and animations
- Interactive elements (Chart.js, clickable buttons) in Markdown variant
- All slides include speaker notes in Markdown format

## License

Apache License 2.0

