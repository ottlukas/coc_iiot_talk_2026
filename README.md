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

The PDF export script can be executed from the repository root or from any subdirectory inside the repo.

### From the project root

```bash
python scripts/export_to_pdf.py docs/presentation.adoc
```

### From a nested directory such as `.venv`

```bash
cd .venv
python ../scripts/export_to_pdf.py ../docs/presentation.adoc
```

### Notes

* The script resolves input paths relative to the current working directory, and it falls back to the repository root when needed.
* The default output location is `docs/exports/presentation.pdf`.
* If Node.js is installed under a non-standard executable name, you can set it with the `NODE_EXECUTABLE` environment variable:

```bash
export NODE_EXECUTABLE=/usr/bin/nodejs
python scripts/export_to_pdf.py docs/presentation.adoc
```

* If you want to provide a custom PDF path, use `--output`:

```bash
python scripts/export_to_pdf.py docs/presentation.adoc --output docs/exports/presentation.pdf
```

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
