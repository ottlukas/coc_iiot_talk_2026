# Reveal.js Docker Setup for AsciiDoc Presentations

This repository contains a complete, Dockerized toolchain for creating and presenting AsciiDoc-based slides using [Reveal.js](https://revealjs.com/). It is pre-configured to align with the Apache Software Foundation's training presentation structure, including automated live reloading in your browser as you edit.

---

## ⚡ Features

1. **AsciiDoc Support:** Write presentation content as plain text using semantic AsciiDoc syntax.
2. **Apache-Aligned Styling:** Includes a custom theme (`apache.css`) loaded via the `:revealjs_theme: apache` attribute.
3. **Live Reloading:** Editing `.adoc` or `.css` files compiles the presentation and reloads the browser automatically.
4. **Offline Capability:** Bundles the full `reveal.js` library locally so the server runs completely offline.
5. **Cross-Platform:** Out-of-the-box configurations for Windows (PowerShell, Command Prompt, WSL2), macOS, and Linux.

---

## 🚀 Quick Start (Using Docker Compose)

The easiest way to build and run the presentation server is using Docker Compose:

```bash
# Build and start the container
docker compose -f docker/dev/docker-compose.yml up --build
```

Once running, open your browser and navigate to:
👉 **[http://localhost:4200](http://localhost:4200)**

---

## 🐳 Running with Raw Docker (Cross-Platform)

If you prefer to run using raw Docker commands, follow the syntax for your specific operating system to ensure volume mounting works correctly.

### 1. Build the Docker Image
```bash
docker build -f docker/dev/Dockerfile -t asciidoc-revealjs-presentation .
```

### 2. Run the Container
*   **Linux / macOS (bash/zsh):**
    ```bash
    docker run --rm -it -p 4200:4200 -v "$(pwd)/docs":/app/docs asciidoc-revealjs-presentation
    ```

> Note: The Docker image installs emoji-capable system fonts so reveal.js slides containing emoji render correctly in PDF export.
*   **Windows (PowerShell):**
    ```powershell
    docker run --rm -it -p 4200:4200 -v "${PWD}/docs":/app/docs asciidoc-revealjs-presentation
    ```
*   **Windows (Command Prompt - CMD):**
    ```cmd
    docker run --rm -it -p 4200:4200 -v "%cd%/docs":/app/docs asciidoc-revealjs-presentation
    ```

---

## ✏️ How to Edit and Present

### Editing Slides
1. Open `docs/presentation.adoc` in your editor.
2. Make your edits (e.g., adding bullets, slides, or speaker notes).
3. Save the file. The browser tab open at `http://localhost:4200` will reload automatically within a second!

### Editing Style & Theme
1. Open `docs/theme/apache.css` in your editor.
2. Edit CSS styles (such as `--r-heading-color` or layout variables).
3. Save the file. The styling modifications will reload instantly.

### Presenting (Speaker Notes & Tools)
* Press **`F`** to toggle full-screen mode.
* Press **`O`** to toggle overview mode (see all slides).
* Press **`S`** to open the **Speaker View** window. This opens a separate window showing:
  * Current slide and next slide preview.
  * Time elapsed and clock.
  * Your speaker notes (defined via `[.notes]` blocks in the `.adoc` source).

---

## 🛠️ Local Build (Without Docker)

You can also run the toolchain directly on your host machine if you have Node.js (v18+) installed:

```bash
# 1. Install dependencies
npm install

# 2. Start the development watcher & live-reload server
npm run dev

# 3. Perform a single production compilation (output in /public)
npm run build
```

## 📄 Export Presentation to PDF

The PDF export flow is fully containerized and uses [Decktape](https://github.com/astefanutti/decktape) inside Docker for stable, presentation-framework-aware rendering. No local installations of Node.js, Puppeteer, Chromium, Ruby, or Asciidoctor are required on the host system.

### Why Decktape?
We migrated from direct Puppeteer scripting to Decktape because:
1. **Reveal.js Awareness**: Decktape is built specifically to export presentations and understands reveal.js slide transitions and fragments.
2. **Reduced Complexity**: It eliminates fragile custom browser automation logic, resulting in reliable outputs.
3. **Better Quality**: Slides are printed exactly as they appear in the browser, applying stylesheet themes and images without spacing regressions.

### Usage

Run the exporter from the project root using:

#### Windows PowerShell:
```powershell
python export_presentation.py --source docs/presentation.adoc --output-dir output
```

#### Linux / macOS:
```bash
python export_presentation.py --source docs/presentation.adoc --output-dir output
```

#### Nested Directory:
The exporter resolves all relative paths correctly even when invoked from a nested directory (e.g. inside virtual environments):
```bash
cd .venv
python ../export_presentation.py --source ../docs/presentation.adoc --output-dir ../output
```

### Options

- `--source`: Path to the source AsciiDoc presentation (default: `docs/presentation.adoc`).
- `--images-dir`: Path to the images directory (default: `docs/images`).
- `--stylesheet`: Path to the custom stylesheet (default: `docs/theme/apache.css`).
- `--output-dir`: Directory to write outputs (default: `output`).
- `--size`: Viewport dimensions for slide rendering (default: `1920x1080`).
- `--pause`: Delay in milliseconds to wait after each slide load (default: `1000`). Use higher values (e.g., `2000`) if images take time to load.
- `--include-empty-notes`: Include speaker note pages in the notes handout PDF even for slides that don't have notes.
- `--ignore-missing-images`: Proceed with the export even if some referenced images are missing.
- `--verbose`: Enable detailed debug logging.

### Generated Outputs

- **`output/presentation.pdf`**: Slide-only PDF suitable for presenting.
- **`output/presentation-with-notes.pdf`**: Speaker-notes handout PDF containing each slide followed by a notes page (interleaved layout).
- **`output/presentation.html`**: Generated Reveal.js HTML slide file, useful for debugging layout.
- **`output/export-report.json`**: Machine-readable JSON report detailing status, execution logs, warnings, and missing images validation.
- **`output/export.log`**: Human-readable execution log.

> [!NOTE]
> The old exporter script (`scripts/export_to_pdf.py`) has been deprecated. If run, it prints a deprecation warning and automatically delegates its arguments to the new `export_presentation.py` script.

---

### 🔧 Troubleshooting

#### 1. Images not visible in the exported PDF
- Ensure the image exists in `docs/images/` and is referenced correctly in `presentation.adoc`.
- Check `output/export-report.json` for validation results under `images_validation`. Any missing images will be listed there.
- Try increasing the page render pause using `--pause 2000` to allow sluggish images to load before Decktape captures the slide.

#### 2. Docker cannot reach the host HTTP server
- **Windows / macOS**: The exporter serves the HTML presentation locally and points Decktape to `http://host.docker.internal:<port>`. Ensure your Docker Desktop configuration allows connections to `host.docker.internal`.
- **Linux**: The exporter runs with `--network host` and serves on `127.0.0.1`. Ensure no firewalls are blocking connections on the dynamic port.

#### 3. Custom theme `apache.css` is not applying
- Ensure the stylesheet file exists at `docs/theme/apache.css` (or the path passed in `--stylesheet`).
- The exporter checks the generated HTML and automatically links the stylesheet as a fallback if it is missing.

#### 4. Decktape execution timeout
- If the Docker runs are slow or download/setup takes time, increase the timeout using `--timeout 240`.

#### 5. Fonts, icons, or emoji are not rendering correctly
- The exporter compiles HTML using `asciidoctor/docker-asciidoctor`. If you are offline, certain web fonts or icons might fail to fetch. If you require specialized system fonts, ensure they are packaged or that you have active internet connectivity during the run.

---

## 📂 Project Structure

```text
coc_iiot_talk_2026/
├── README.md                       # This guide
├── package.json                    # Node.js dependencies & scripts
│
├── docs/                           # AsciiDoc source files & assets
│   ├── presentation.adoc           # Main slide source code
│   ├── open-source-manufacturing.md    # Talk content outline
│   ├── open-source-manufacturing-draft.md  # Earlier draft (for reference)
│   ├── images/                     # Slide images & diagrams
│   ├── theme/
│   │   └── apache.css              # Custom presentation stylesheet
│   └── exports/                    # PDF/PPTX exports
│       ├── *.pdf
│       └── *.pptx
│
├── docker/                         # Docker configurations
│   └── dev/
│       ├── docker-compose.yml      # Development compose file
│       ├── Dockerfile              # Development container image
│       └── .dockerignore
│
├── presentations/                  # Additional/archived presentations
│   └── open-source-manufacturing/  # Ruby-based RevealJS setup (legacy)
│       ├── docker-compose.yml
│       ├── Dockerfile
│       ├── slides.adoc
│       └── ...
│
└── scripts/                        # Build & utility scripts
    ├── compile.js                  # AsciiDoc → HTML converter
    ├── watch.js                    # File watcher & live-reload server
    ├── export_to_pdf.py            # Docker-based PDF export helper
    └── organize_repo.py            # Repository cleanup automation
```

---

## 📑 AsciiDoc Slide Syntax Reference

Follow these guidelines for writing your slides:

*   **Slide Headings:**
    *   `== Slide Title` starts a new slide.
    *   `=== Topic Title` makes a subtitle or subheading inside a slide.
*   **Source Code Blocks:**
    ```asciidoc
    [source,sql]
    ----
    SELECT * FROM root.factory1.device1;
    ----
    ```
*   **Speaker Notes:**
    ```asciidoc
    [.notes]
    --
    Your speaker notes go here.
    --
    ```
*   **Takeaway Cards:**
    ```asciidoc
    [.takeaway-box]
    --
    Highlight key metrics or findings here.
    --
    ```
