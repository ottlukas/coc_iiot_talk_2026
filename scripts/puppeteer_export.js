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
