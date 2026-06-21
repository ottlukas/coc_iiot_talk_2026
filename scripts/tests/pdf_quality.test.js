const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const OUTPUT_DIR = path.join(__dirname, 'outputs');

describe('PDF/typography quality (basic checks)', () => {
  let browser;

  beforeAll(async () => {
    browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    // ensure outputs dir exists for debug artifacts
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }, 20000);

  afterAll(async () => {
    if (browser) await browser.close();
  });

  it('ensures representative elements have normal word/letter spacing', async () => {
    const cssPath = path.join(__dirname, '..', '..', 'docs', 'theme', 'apache.css');
    const css = fs.readFileSync(cssPath, 'utf8');

    const page = await browser.newPage();
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
      <div class="reveal"><div class="slides">
        <section>
          <h1>Title Slide Example</h1>
          <p>This paragraph should render with normal spacing between words and letters.</p>
          <ul><li>Bullet item one</li><li>Bullet item two</li></ul>
        </section>
      </div></div>
    </body></html>`;

    await page.setContent(html, { waitUntil: 'networkidle0' });
    await page.evaluate(() => (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve());

    const selectors = ['.reveal h1', '.reveal p', '.reveal li'];
    for (const sel of selectors) {
      // capture computed styles
      const styles = await page.$eval(sel, (el) => {
        const cs = window.getComputedStyle(el);
        return { wordSpacing: cs.wordSpacing, letterSpacing: cs.letterSpacing, fontFamily: cs.fontFamily };
      });

      const acceptable = (v) => v === 'normal' || v === '0px' || /^-?0(?:\.0+)?px$/.test(v);
      expect(acceptable(styles.wordSpacing)).toBe(true);
      expect(acceptable(styles.letterSpacing)).toBe(true);
    }

    // Save a screenshot artifact for CI debugging
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'pdf_quality_snapshot.png'), fullPage: true });
    await page.close();
  }, 20000);
});
