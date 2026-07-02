# COC IIoT Talk 2026: Open Source for Regulated Manufacturing

A complete, Dockerized toolchain for creating and presenting AsciiDoc-based slides using [Reveal.js](https://revealjs.com/). This repository contains the presentation materials and infrastructure for the "Open Source for Regulated Manufacturing: GMP-Compliant IIoT Data Logging" talk.

![Apache License 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Node.js](https://img.shields.io/badge/Node.js-20+-green)

---

## \u26a1\ufe0f Features

- **AsciiDoc Support**: Write presentation content as plain text using semantic AsciiDoc syntax
- **Apache-Aligned Styling**: Includes a custom theme (`apache.css`) for professional presentation styling
- **Live Reloading**: Editing `.adoc` or `.css` files compiles the presentation and reloads the browser automatically
- **Offline Capability**: Bundles the full `reveal.js` library locally so the server runs completely offline
- **Cross-Platform**: Out-of-the-box configurations for Windows, macOS, and Linux
- **PDF Export**: Containerized PDF export using Decktape for reliable, presentation-aware rendering

---

## \ud83d\ude80\ufe0f Quick Start (Using Docker Compose)

The easiest way to build and run the presentation server is using Docker Compose:

```bash
# Build and start the container
docker compose -f docker/dev/docker-compose.yml up --build
```

Once running, open your browser and navigate to:
\ud83d\udc49 **[http://localhost:4200](http://localhost:4200)**

---

## \ud83d\udc33 Running with Raw Docker

If you prefer to run using raw Docker commands, follow the syntax for your specific operating system:

### 1. Build the Docker Image
```bash
docker build -f docker/dev/Dockerfile -t coc-iiot-talk-2026 .
```

### 2. Run the Container

**Linux / macOS (bash/zsh):**
```bash
docker run --rm -it -p 4200:4200 -v "$(pwd)/docs":/app/docs -v "$(pwd)/src":/app/src coc-iiot-talk-2026
```

**Windows (PowerShell):**
```powershell
docker run --rm -it -p 4200:4200 -v "${PWD}/docs":/app/docs -v "${PWD}/src":/app/src coc-iiot-talk-2026
```

**Windows (Command Prompt - CMD):**
```cmd
docker run --rm -it -p 4200:4200 -v "%cd%/docs":/app/docs -v "%cd%/src":/app/src coc-iiot-talk-2026
```

> **Note**: The Docker image installs emoji-capable system fonts so reveal.js slides containing emoji render correctly in PDF export.

---

## \u270f\ufe0f How to Edit and Present

### Editing Slides
1. Open `docs/presentation.adoc` in your editor
2. Make your edits (e.g., adding bullets, slides, or speaker notes)
3. Save the file. The browser tab open at `http://localhost:4200` will reload automatically within a second!

### Editing Style & Theme
1. Open `docs/theme/apache.css` in your editor
2. Edit CSS styles (such as `--r-heading-color` or layout variables)
3. Save the file. The styling modifications will reload instantly

### Presenting (Speaker Notes & Tools)
- Press **`F`** to toggle full-screen mode
- Press **`O`** to toggle overview mode (see all slides)
- Press **`S`** to open the **Speaker View** window. This opens a separate window showing:
  - Current slide and next slide preview
  - Time elapsed and clock
  - Your speaker notes (defined via `[.notes]` blocks in the `.adoc` source)

---

## \ud83d\udcc4 Export Presentation to PDF

The PDF export flow is fully containerized and uses [Decktape](https://github.com/astefanutti/decktape) inside Docker for stable, presentation-framework-aware rendering. No local installations of Node.js, Puppeteer, Chromium, Ruby, or Asciidoctor are required on the host system.

### Why Decktape?
We migrated from direct Puppeteer scripting to Decktape because:
1. **Reveal.js Awareness**: Decktape is built specifically to export presentations and understands reveal.js slide transitions and fragments
2. **Reduced Complexity**: It eliminates fragile custom browser automation logic, resulting in reliable outputs
3. **Better Quality**: Slides are printed exactly as they appear in the browser, applying stylesheet themes and images without spacing regressions

### Usage

Run the exporter from the project root using:

```bash
# Basic export
python src/scripts/export_presentation.py

# With custom options
python src/scripts/export_presentation.py \
  --source docs/presentation.adoc \
  --output-dir output \
  --size 1920x1080 \
  --pause 2000
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--source` | Path to the source AsciiDoc presentation | `docs/presentation.adoc` |
| `--images-dir` | Path to the images directory | `docs/images` |
| `--stylesheet` | Path to the custom stylesheet | `docs/theme/apache.css` |
| `--output-dir` | Directory to write outputs | `output` |
| `--size` | Viewport dimensions for slide rendering | `1920x1080` |
| `--pause` | Delay in milliseconds to wait after each slide load | `1000` |
| `--include-empty-notes` | Include speaker note pages in the notes handout PDF even for slides that don't have notes | `False` |
| `--ignore-missing-images` | Proceed with the export even if some referenced images are missing | `False` |
| `--verbose` | Enable detailed debug logging | `False` |
| `--timeout` | Timeout in seconds for Docker operations | `120` |

### Generated Outputs

- **`output/presentation.pdf`**: Slide-only PDF suitable for presenting
- **`output/presentation-with-notes.pdf`**: Speaker-notes handout PDF containing each slide followed by a notes page (interleaved layout)
- **`output/presentation.html`**: Generated Reveal.js HTML slide file, useful for debugging layout
- **`output/export-report.json`**: Machine-readable JSON report detailing status, execution logs, warnings, and missing images validation
- **`output/export.log`**: Human-readable execution log

---

## \ud83d\udcd1 AsciiDoc Slide Syntax Reference

Follow these guidelines for writing your slides:

### Slide Structure
```asciidoc
== Main Slide Title

This is the content of the first slide.

=== Subsection Title

This creates a subsection within the same slide.

== Another Slide

This starts a new slide.
```

### Source Code Blocks
```asciidoc
[source,sql]
----
SELECT * FROM root.factory1.device1;
----
```

### Speaker Notes
```asciidoc
[.notes]
--
Your speaker notes go here.
These are only visible in speaker view.
--
```

### Takeaway Cards
```asciidoc
[.takeaway-box]
--
Highlight key metrics or findings here.
This creates a styled callout box.
--
```

### Images
```asciidoc
image::images/demo.jpeg[Demo Image,800,600]
```

### Lists
```asciidoc
* Bullet point 1
* Bullet point 2
** Nested bullet

. Numbered list item 1
. Numbered list item 2
```

---

## \ud83d\udcc2 Project Structure

```text
coc_iiot_talk_2026/
├── README.md                          # This guide
├── LICENSE                            # Apache License 2.0
├── .gitignore                         # Git ignore patterns
├── .dockerignore                      # Docker ignore patterns
├── package.json                       # Node.js dependencies & scripts
├── docker/
│   └── dev/
│       ├── Dockerfile                 # Development container image
│       ├── docker-compose.yml         # Development compose file
│       └── .dockerignore              # Docker-specific ignore patterns
├── docs/
│   ├── presentation.adoc              # Main slide source code
│   ├── images/                        # Slide images & diagrams
│   │   ├── alcoa.jpeg
│   │   ├── apachestack.jpeg
│   │   ├── balance.jpeg
│   │   └── ... (other presentation images)
│   └── theme/
│       └── apache.css                 # Custom presentation stylesheet
└── src/
    ├── scripts/
    │   ├── compile.js                 # AsciiDoc → HTML converter
    │   ├── watch.js                   # File watcher & live-reload server
    │   ├── export_presentation.py     # Main PDF export script (Decktape-based)
    │   └── export_to_pdf.py           # DEPRECATED: Legacy exporter (delegates to new script)
    └── exporter/
        ├── asciidoc_parser.py         # AsciiDoc parsing utilities
        ├── config.py                  # Export configuration
        ├── decktape_exporter.py       # Decktape export functionality
        ├── docker_utils.py            # Docker utility functions
        ├── html_builder.py            # HTML compilation utilities
        ├── http_server.py             # Temporary HTTP server for export
        ├── pdf_utils.py               # PDF generation utilities
        └── reporting.py               # Export reporting and logging
    └── tests/
        ├── test_asciidoc_parser.py    # AsciiDoc parser tests
        ├── test_deprecated_exporter.py # Legacy exporter tests
        ├── test_docker_commands.py    # Docker command tests
        └── test_paths.py              # Path resolution tests
```

---

## \ud83d\udd27 Troubleshooting

### 1. Images not visible in the exported PDF
- Ensure the image exists in `docs/images/` and is referenced correctly in `presentation.adoc`
- Check `output/export-report.json` for validation results under `images_validation`. Any missing images will be listed there
- Try increasing the page render pause using `--pause 2000` to allow sluggish images to load before Decktape captures the slide

### 2. Docker cannot reach the host HTTP server
- **Windows / macOS**: The exporter serves the HTML presentation locally and points Decktape to `http://host.docker.internal:<port>`. Ensure your Docker Desktop configuration allows connections to `host.docker.internal`
- **Linux**: The exporter runs with `--network host` and serves on `127.0.0.1`. Ensure no firewalls are blocking connections on the dynamic port

### 3. Custom theme `apache.css` is not applying
- Ensure the stylesheet file exists at `docs/theme/apache.css` (or the path passed in `--stylesheet`)
- The exporter checks the generated HTML and automatically links the stylesheet as a fallback if it is missing

### 4. Decktape execution timeout
- If the Docker runs are slow or download/setup takes time, increase the timeout using `--timeout 240`

### 5. Fonts, icons, or emoji are not rendering correctly
- The exporter compiles HTML using `asciidoctor/docker-asciidoctor`. If you are offline, certain web fonts or icons might fail to fetch
- If you require specialized system fonts, ensure they are packaged or that you have active internet connectivity during the run

---

## \ud83d\udc68\u200d\ud83d\udcbb Development

### Local Build (Without Docker)

You can also run the toolchain directly on your host machine if you have Node.js (v18+) installed:

```bash
# 1. Install dependencies
npm install

# 2. Start the development watcher & live-reload server
npm run dev

# 3. Perform a single production compilation (output in /public)
npm run build

# 4. Export to PDF
npm run export:pdf
```

### Running Tests

```bash
# Run all tests
npm test

# Run only Python tests
npm run test:python

# Run only JavaScript tests
npm run test:js
```

### Clean Generated Files

```bash
npm run clean
```

---

## \ud83c\udf1f Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow the existing code style** and patterns
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description of your changes

---

## \ud83e\uddd6 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## \ud83d\udc81 Acknowledgments

- [Reveal.js](https://revealjs.com/) - The HTML presentation framework
- [AsciiDoc](https://asciidoc.org/) - The text document format for writing presentations
- [Decktape](https://github.com/astefanutti/decktape) - PDF export for reveal.js presentations
- [Docker](https://www.docker.com/) - Container platform for consistent environments

---

## \ud83d\udcf0 Contact

For questions or issues related to this presentation or toolchain, please refer to the repository issues or contact the maintainer.

**Maintainer**: Lukas Ott
**Repository**: [ottlukas/coc_iiot_talk_2026](https://github.com/ottlukas/coc_iiot_talk_2026)