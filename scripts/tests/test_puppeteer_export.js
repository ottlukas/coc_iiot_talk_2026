const fs = require('fs');
const os = require('os');
const path = require('path');
const { exportToPdf, appendPrintPdfQuery } = require('../puppeteer_export');

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

  it('calls page.pdf with correct parameters', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
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

    expect(page.pdf).toHaveBeenCalledWith({
      path: outputPath,
      format: 'A4',
      printBackground: true,
    });
    expect(browser.close).toHaveBeenCalled();
  });

  it('creates output directory if missing', async () => {
    const page = {
      setDefaultNavigationTimeout: jest.fn(),
      goto: jest.fn().mockResolvedValue(undefined),
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
