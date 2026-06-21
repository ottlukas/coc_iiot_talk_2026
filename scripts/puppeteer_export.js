const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const DEFAULT_URL = 'http://localhost:4200';
const DEFAULT_OUTPUT = path.join(__dirname, '..', 'docs', 'exports', 'presentation.pdf');
const DEFAULT_TIMEOUT = 30000;

function parseArgs(argv) {
  const args = argv.slice(2);
  let url = DEFAULT_URL;
  let output = DEFAULT_OUTPUT;

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
    throw new Error(`Unknown argument: ${arg}`);
  }

  return { url, output };
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
  const resolvedOutput = path.resolve(outputPath);
  ensureOutputDirectory(resolvedOutput);

  const pageUrl = appendPrintPdfQuery(url);
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
      content: `
        html, body, .reveal, .reveal .slides, .reveal section,
        .reveal h1, .reveal h2, .reveal h3, .reveal h4, .reveal h5, .reveal h6,
        .reveal p, .reveal li, .reveal blockquote, .reveal code {
          font-family: var(--r-main-font), "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", system-ui, -apple-system, sans-serif !important;
        }
      `,
    });
    await page.evaluate(async () => {
      await document.fonts.ready;
    });
    // Ensure the page is rendered using screen styles so the PDF matches the on-screen HTML
    if (page.emulateMediaType) {
      await page.emulateMediaType('screen');
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
  const { url, output } = parseArgs(argv || process.argv);
  await exportToPdf(url, output);
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
