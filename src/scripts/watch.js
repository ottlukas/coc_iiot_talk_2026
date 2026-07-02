const chokidar = require('chokidar');
const liveServer = require('live-server');
const { execSync } = require('child_process');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const SLIDES_DIR = path.join(ROOT_DIR, 'docs');
const PUBLIC_DIR = path.join(ROOT_DIR, 'public');

// Helper to run compiler
let isCompiling = false;
function compileSlides() {
  if (isCompiling) return;
  isCompiling = true;

  console.log(`\n[${new Date().toLocaleTimeString()}] Change detected, recompiling...`);
  try {
    execSync('node ' + path.join(__dirname, 'compile.js'), { stdio: 'inherit', cwd: ROOT_DIR });
    console.log(`[${new Date().toLocaleTimeString()}] Recompile complete.`);
  } catch (err) {
    console.error(`[${new Date().toLocaleTimeString()}] Compilation failed:`, err.message);
  } finally {
    isCompiling = false;
  }
}

// 1. Initial compile
console.log('--- Initial Build ---');
compileSlides();

// 2. Setup file watcher
console.log(`\nWatching for changes in: ${SLIDES_DIR}`);
const watcher = chokidar.watch(SLIDES_DIR, {
  ignored: /(^|[\/\\])\../, // ignore dotfiles/folders
  persistent: true,
  ignoreInitial: true,
  // Add polling fallback for VM/Docker volumes
  usePolling: true,
  interval: 1000,
  binaryInterval: 3000
});

watcher.on('all', (event, filePath) => {
  console.log(`[Watcher] Event '${event}' on file: ${path.relative(__dirname, filePath)}`);
  compileSlides();
});

// 3. Start development server
const port = process.env.PORT || 4200;
const host = '0.0.0.0';

const serverParams = {
  port: parseInt(port, 10),
  host: host,
  root: PUBLIC_DIR,
  open: false, // Don't open browser inside container
  file: 'index.html',
  wait: 500, // wait time before reload injection
  logLevel: 1 // only errors and restarts
};

console.log(`Starting live-reload server at http://localhost:${port}...`);
liveServer.start(serverParams);
