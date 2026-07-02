const fs = require('fs-extra');
const path = require('path');
const asciidoctor = require('@asciidoctor/core')();
const asciidoctorRevealjs = require('@asciidoctor/reveal.js');

// Register the reveal.js converter with Asciidoctor.js
asciidoctorRevealjs.register();

const ROOT_DIR = path.join(__dirname, '..');
const PUBLIC_DIR = path.join(ROOT_DIR, 'public');
const SLIDES_DIR = path.join(ROOT_DIR, 'docs');
const REVEAL_DEST = path.join(PUBLIC_DIR, 'reveal.js');

try {
  console.log('[Build] Starting presentation compilation...');

  // 1. Ensure public directory structure exists
  fs.ensureDirSync(PUBLIC_DIR);
  fs.ensureDirSync(REVEAL_DEST);

  // 2. Copy reveal.js core assets from node_modules
  const revealSourceDist = path.join(ROOT_DIR, 'node_modules', 'reveal.js', 'dist');
  const revealSourcePlugin = path.join(ROOT_DIR, 'node_modules', 'reveal.js', 'plugin');

  if (fs.existsSync(revealSourceDist)) {
    fs.copySync(revealSourceDist, path.join(REVEAL_DEST, 'dist'));
  } else {
    throw new Error('reveal.js dist files not found in node_modules');
  }

  if (fs.existsSync(revealSourcePlugin)) {
    fs.copySync(revealSourcePlugin, path.join(REVEAL_DEST, 'plugin'));
  } else {
    throw new Error('reveal.js plugin files not found in node_modules');
  }

  // 3. Copy slides images if they exist
  const imagesSource = path.join(SLIDES_DIR, 'images');
  const imagesDest = path.join(PUBLIC_DIR, 'images');
  if (fs.existsSync(imagesSource)) {
    fs.copySync(imagesSource, imagesDest);
    console.log('[Build] Images copied successfully.');
  }

  // 4. Copy custom apache theme if it exists
  const customThemeSource = path.join(SLIDES_DIR, 'theme', 'apache.css');
  const customThemeDest = path.join(REVEAL_DEST, 'dist', 'theme', 'apache.css');
  if (fs.existsSync(customThemeSource)) {
    fs.ensureDirSync(path.dirname(customThemeDest));
    fs.copySync(customThemeSource, customThemeDest);
    console.log('[Build] Custom Apache theme copied successfully.');
  } else {
    console.log('[Build] Warning: docs/theme/apache.css not found, custom styling will not apply.');
  }

  // 5. Compile presentation.adoc
  const adocFile = path.join(SLIDES_DIR, 'presentation.adoc');
  if (!fs.existsSync(adocFile)) {
    throw new Error(`AsciiDoc source file not found at: ${adocFile}`);
  }

  console.log('[Build] Converting presentation.adoc to HTML...');
  asciidoctor.convertFile(adocFile, {
    safe: 'unsafe',
    backend: 'revealjs',
    to_dir: PUBLIC_DIR,
    to_file: 'index.html',
    attributes: {
      // Point reveal.js assets relative to the compiled HTML
      'revealjsdir': 'reveal.js'
    }
  });

  console.log('[Build] Compilation complete! Output generated in public/index.html');
} catch (error) {
  console.error('[Build] Compilation failed with error:', error.message);
  process.exit(1);
}
