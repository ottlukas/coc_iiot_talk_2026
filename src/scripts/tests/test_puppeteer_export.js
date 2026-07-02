const fs = require('fs');
const os = require('os');
const path = require('path');
const { exportToPdf, appendPrintPdfQuery, parseArgs } = require('../puppeteer_export');

jest.mock('puppeteer', () => ({
  launch: jest.fn(),
}));

const puppeteer = require('puppeteer');

describe('puppeteer_export', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('appends ?print-pdf to the URL', () => {
    expect(appendPrintPdfQuery('http://localhost:4200')).toBe('http://localhost:4200?print-pdf');
    expect(appendPrintPdfQuery('http://localhost:4200?foo=bar')).toBe('http://localhost:4200?foo=bar&print-pdf');
    expect(appendPrintPdfQuery('http://localhost:4200#slide-1')).toBe('http://localhost:4200?print-pdf#slide-1');
  });

  it('includes emoji fallback fonts in the reveal theme', () => {
    const themeCss = fs.readFileSync(path.join(__dirname, '..', '..', 'docs', 'theme', 'apache.css'), 'utf8');
    expect(themeCss).toMatch(/Segoe UI Emoji/);
    expect(themeCss).toMatch(/Apple Color Emoji/);
    expect(themeCss).toMatch(/Noto Color Emoji/);
  });

  it('calls page.pdf with correct parameters', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
      addStyleTag: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue(undefined),
      pdf: jest.fn().mockResolvedValue(undefined),
    };
    const browser = {
      newPage: jest.fn().mockResolvedValue(page),
      close: jest.fn().mockResolvedValue(undefined),
    };
    puppeteer.launch.mockResolvedValue(browser);

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputPath = path.join(tempDir, 'docs', 'exports', 'presentation.pdf');

    await exportToPdf('http://localhost:4200', outputPath);

    // Ensure the theme css was injected (contains emoji fallback fonts)
    expect(page.addStyleTag).toHaveBeenCalledWith(expect.objectContaining({ content: expect.stringContaining('Segoe UI Emoji') }));
    // And ensure we added print/transform override to prevent scaled text metrics
    expect(page.addStyleTag).toHaveBeenCalledWith(expect.objectContaining({ content: expect.stringContaining('transform: none') }));
    expect(page.evaluate).toHaveBeenCalledWith(expect.any(Function));
    expect(page.pdf).toHaveBeenCalledWith({
      path: outputPath,
      format: 'A4',
      printBackground: true,
    });
    expect(browser.close).toHaveBeenCalled();
  });

  it('waits for document fonts to be ready before generating PDF', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
      addStyleTag: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue(undefined),
      pdf: jest.fn().mockResolvedValue(undefined),
    };
    const browser = {
      newPage: jest.fn().mockResolvedValue(page),
      close: jest.fn().mockResolvedValue(undefined),
    };
    puppeteer.launch.mockResolvedValue(browser);

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputPath = path.join(tempDir, 'docs', 'exports', 'presentation.pdf');

    await exportToPdf('http://localhost:4200', outputPath);

    expect(page.evaluate).toHaveBeenCalledTimes(1);
    expect(page.pdf).toHaveBeenCalledWith({
      path: outputPath,
      format: 'A4',
      printBackground: true,
    });
  });

  it('parses --mode argument correctly', () => {
    const args = parseArgs(['node', 'script', '--url', 'http://localhost:4200', '--output', '/tmp/out.pdf', '--mode', 'notes']);
    expect(args.mode).toBe('notes');
    expect(args.url).toBe('http://localhost:4200');
    expect(args.output).toBe('/tmp/out.pdf');
  });

  it('generates notes-mode PDF by transforming DOM', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
      addStyleTag: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue(undefined),
      pdf: jest.fn().mockResolvedValue(undefined),
    };
    const browser = {
      newPage: jest.fn().mockResolvedValue(page),
      close: jest.fn().mockResolvedValue(undefined),
    };
    puppeteer.launch.mockResolvedValue(browser);

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputPath = path.join(tempDir, 'docs', 'exports', 'presentation-notes.pdf');

    await exportToPdf('http://localhost:4200', outputPath, 'notes');

    expect(page.evaluate).toHaveBeenCalled();
    expect(page.pdf).toHaveBeenCalledWith({
      path: outputPath,
      format: 'A4',
      printBackground: true,
    });
  });

  it('throws when images failed to load in slides mode', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
      addStyleTag: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue(['/bad/image.png']),
      pdf: jest.fn().mockResolvedValue(undefined),
    };
    const browser = {
      newPage: jest.fn().mockResolvedValue(page),
      close: jest.fn().mockResolvedValue(undefined),
    };
    puppeteer.launch.mockResolvedValue(browser);

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputPath = path.join(tempDir, 'docs', 'exports', 'presentation.pdf');

    await expect(exportToPdf('http://localhost:4200', outputPath, 'slides')).rejects.toThrow('Some images failed to load');
  });

  it('creates output directory if missing', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
      evaluate: jest.fn().mockResolvedValue(undefined),
      pdf: jest.fn().mockResolvedValue(undefined),
    };
    const browser = {
      newPage: jest.fn().mockResolvedValue(page),
      close: jest.fn().mockResolvedValue(undefined),
    };
    puppeteer.launch.mockResolvedValue(browser);

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputDir = path.join(tempDir, 'docs', 'exports');
    const outputPath = path.join(outputDir, 'presentation.pdf');

    await exportToPdf('http://localhost:4200', outputPath);

    expect(fs.existsSync(outputDir)).toBe(true);
    expect(browser.close).toHaveBeenCalled();
  });

  it('throws when puppeteer launch fails', async () => {
    puppeteer.launch.mockRejectedValue(new Error('launch failed'));

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ppt-export-'));
    const outputPath = path.join(tempDir, 'docs', 'exports', 'presentation.pdf');

    await expect(exportToPdf('http://localhost:4200', outputPath)).rejects.toThrow('Failed to generate PDF: launch failed');
  });
});
