const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const DEFAULT_URL = 'http://localhost:4200';
const DEFAULT_OUTPUT = path.join(__dirname, '..', 'docs', 'exports', 'presentation.pdf');
const DEFAULT_TIMEOUT = 30000;
const DEFAULT_MODE = 'slides'; // other valid value: 'notes'

function parseArgs(argv) {
  const args = argv.slice(2);
  let url = DEFAULT_URL;
  let output = DEFAULT_OUTPUT;
  let mode = DEFAULT_MODE;

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--url' && args[i + 1]) {
      url = args[++i];
      continue;
    }
    if (arg === '--output' && args[i + 1]) {
      output = args[++i];
      continue;
    }
    if (arg === '--mode' && args[i + 1]) {
      mode = args[++i];
      continue;
    }
    throw new Error(`Unknown argument: ${arg}`);
  }

  return { url, output, mode };
}

function appendPrintPdfQuery(url) {
  const [baseUrl, hash = ''] = url.split('#');
  const [pathname, query] = baseUrl.split('?');
  const queryString = query ? `?${query}` : '';
  const separator = query ? '&' : '?';
  return `${pathname}${queryString}${separator}print-pdf${hash ? `#${hash}` : ''}`;
}

function ensureOutputDirectory(outputPath) {
  const directory = path.dirname(outputPath);
  fs.mkdirSync(directory, { recursive: true });
}

function findChromiumExecutable() {
  const candidates = [
    process.env.CHROME_PATH,
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
  ].filter(Boolean);
  return candidates.find((candidate) => fs.existsSync(candidate));
}

async function exportToPdf(url, outputPath) {
  // Backwards compatible signature: exportToPdf(url, outputPath) or
  // newer signature: exportToPdf(url, outputPath, mode)
  const mode = arguments.length >= 3 ? arguments[2] : DEFAULT_MODE;
  const resolvedOutput = path.resolve(outputPath);
  ensureOutputDirectory(resolvedOutput);

  // For slides mode we want reveal's print-pdf rendering
  const pageUrl = mode === 'slides' ? appendPrintPdfQuery(url) : url;
  const launchOptions = {
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  };

  const chromiumPath = findChromiumExecutable();
  if (chromiumPath) {
    launchOptions.executablePath = chromiumPath;
  }

  let browser;
  try {
    browser = await puppeteer.launch(launchOptions);
    const page = await browser.newPage();
    page.setDefaultNavigationTimeout(DEFAULT_TIMEOUT);
    await page.goto(pageUrl, { waitUntil: 'networkidle2', timeout: DEFAULT_TIMEOUT });
    await page.addStyleTag({
      content: (function() {
        try {
          const themePath = path.join(__dirname, '..', 'docs', 'theme', 'apache.css');
          let themeCss = '';
          if (fs.existsSync(themePath)) {
            themeCss = fs.readFileSync(themePath, 'utf8');
          }
          // Add PDF/print-specific overrides to avoid renderer spacing regressions
          const printOverrides = `
            html, body, .reveal, .reveal .slides, .reveal section,
            .reveal h1, .reveal h2, .reveal h3, .reveal h4, .reveal h5, .reveal h6,
            .reveal p, .reveal li, .reveal blockquote, .reveal code {
              font-family: var(--r-main-font), "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", system-ui, -apple-system, sans-serif !important;
              word-spacing: normal !important;
              letter-spacing: normal !important;
              text-rendering: optimizeLegibility !important;
              -webkit-font-smoothing: antialiased !important;
              -moz-osx-font-smoothing: grayscale !important;
              font-kerning: normal !important;
              font-feature-settings: normal !important;
            }
            /* Remove transforms during print to avoid scaled text metric changes */
            .reveal, .reveal .slides, .reveal .slides section { transform: none !important; }
            @media print {
              .reveal, .reveal .slides, .reveal .slides section { transform: none !important; }
            }
          `;

          return themeCss + '\n' + printOverrides;
        } catch (e) {
          return `
            html, body, .reveal, .reveal .slides, .reveal section,
            .reveal h1, .reveal p, .reveal li { font-family: system-ui, -apple-system, sans-serif !important; }
          `;
        }
      })(),
    });
    await page.evaluate(async () => {
      await document.fonts.ready;
    });
    // Ensure the page is rendered using screen styles so the PDF matches the on-screen HTML
    if (page.emulateMediaType) {
      await page.emulateMediaType('screen');
    }
    // Trigger lazy-loading images (common in Reveal.js slides) by copying
    // `data-src`/`data-lazy` attributes to `src` so the browser starts loading
    // them even if they are not in the active slide.
    await page.evaluate(() => {
      const lazyAttrs = ['data-src', 'data-lazy', 'data-lazy-src', 'data-srcset'];
      Array.from(document.images || []).forEach((img) => {
        for (const attr of lazyAttrs) {
          const v = img.getAttribute && img.getAttribute(attr);
          if (v) {
            if (attr === 'data-srcset') img.srcset = v;
            else img.src = v;
          }
        }
      });
    });

    // Wait for images to be ready before printing. If any images fail to load,
    // collect their URLs and fail deterministically so CI can catch problems.
    const failedImages = await page.evaluate(() => {
      const imgs = Array.from(document.images || []);
      return Promise.all(imgs.map((img) => {
        // If already complete and naturalWidth > 0, consider it ok
        if (img.complete && img.naturalWidth && img.naturalWidth > 0) return null;
        return new Promise((resolve) => {
          const onLoad = () => resolve(null);
          const onError = () => resolve(img.src || img.currentSrc || '<unknown>');
          img.addEventListener('load', onLoad, { once: true });
          img.addEventListener('error', onError, { once: true });
          // Fallback timeout per image
          setTimeout(() => resolve(img.src || img.currentSrc || '<unknown>'), 5000);
        });
      })).then(results => results.filter(Boolean));
    });

    if (mode === 'slides' && failedImages && failedImages.length) {
      throw new Error(`Some images failed to load before PDF generation: ${failedImages.join(', ')}`);
    }

    if (mode === 'notes') {
      // Build a simple printable notes layout derived from the reveal DOM.
      await page.evaluate(() => {
        const slides = Array.from(document.querySelectorAll('.reveal .slides section'));
        const container = document.createElement('div');
        container.style.padding = '20px';
        container.style.fontFamily = 'system-ui, -apple-system, sans-serif';
        slides.forEach((section, idx) => {
          const titleEl = section.querySelector('h1, h2, h3, h4') || document.createElement('div');
          const notesEl = section.querySelector('.notes');
          const pageDiv = document.createElement('section');
          const h = document.createElement('h2');
          h.textContent = `${idx + 1}. ${titleEl.textContent || 'Slide'}`;
          h.style.marginTop = '24px';
          h.style.marginBottom = '8px';
          pageDiv.appendChild(h);
          if (notesEl) {
            const p = document.createElement('div');
            p.innerHTML = notesEl.innerHTML;
            p.style.whiteSpace = 'pre-wrap';
            p.style.fontSize = '12pt';
            pageDiv.appendChild(p);
          } else {
            const p = document.createElement('div');
            p.textContent = '(no notes)';
            p.style.opacity = '0.6';
            pageDiv.appendChild(p);
          }
          container.appendChild(pageDiv);
        });
        document.body.innerHTML = '';
        document.body.appendChild(container);
      });
    }

    await page.pdf({ path: resolvedOutput, format: 'A4', printBackground: true });
    console.log(`Exported PDF to: ${resolvedOutput}`);
  } catch (error) {
    throw new Error(`Failed to generate PDF: ${error.message}`);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

async function main(argv) {
  const { url, output, mode } = parseArgs(argv || process.argv);
  await exportToPdf(url, output, mode);
}

module.exports = {
  appendPrintPdfQuery,
  exportToPdf,
  parseArgs,
};

if (require.main === module) {
  main().catch((error) => {
    console.error(error.message);
    process.exit(1);
  });
}
