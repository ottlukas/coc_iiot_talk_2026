const fs = require('fs');
const chokidar = require('chokidar');
const liveServer = require('live-server');
const { execSync } = require('child_process');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..', '..');
const SLIDES_DIR = path.join(ROOT_DIR, 'docs');
const PUBLIC_DIR = path.join(ROOT_DIR, 'public');

function getServerParams() {
  const port = parseInt(process.env.PORT || 4200, 10);
  return {
    port,
    host: '0.0.0.0',
    root: PUBLIC_DIR,
    open: false,
    file: 'index.html',
    wait: 500,
    logLevel: 1
  };
}

function logPaths() {
  console.log('[Paths] ROOT_DIR =', ROOT_DIR);
  console.log('[Paths] SLIDES_DIR =', SLIDES_DIR);
  console.log('[Paths] PUBLIC_DIR =', PUBLIC_DIR);
}

function logPublicFiles() {
  try {
    const files = fs.readdirSync(PUBLIC_DIR);
    console.log('[Paths] public directory contents:', files);
  } catch (err) {
    console.warn('[Paths] Unable to list public directory:', err.message);
  }
}

// Helper to run compiler
let isCompiling = false;
function compileSlides() {
  if (isCompiling) return;
  isCompiling = true;

  console.log(`\n[${new Date().toLocaleTimeString()}] Change detected, recompiling...`);
  try {
    execSync('node ' + path.join(__dirname, 'compile.js'), { stdio: 'inherit', cwd: ROOT_DIR });
    logPublicFiles();
    console.log(`[${new Date().toLocaleTimeString()}] Recompile complete.`);
  } catch (err) {
    console.error(`[${new Date().toLocaleTimeString()}] Compilation failed:`, err.message);
  } finally {
    isCompiling = false;
  }
}

function startWatcher() {
  console.log(`\nWatching for changes in: ${SLIDES_DIR}`);
  const watcher = chokidar.watch(SLIDES_DIR, {
    ignored: /(^|[\/\\])\../,
    persistent: true,
    ignoreInitial: true,
    usePolling: true,
    interval: 1000,
    binaryInterval: 3000
  });

  watcher.on('all', (event, filePath) => {
    console.log(`[Watcher] Event '${event}' on file: ${path.relative(__dirname, filePath)}`);
    compileSlides();
  });
}

function startServer() {
  const serverParams = getServerParams();
  console.log('[Server] live-server configuration:', serverParams);
  console.log(`Starting live-reload server at http://localhost:${serverParams.port}...`);
  liveServer.start(serverParams);
}

function init() {
  logPaths();
  console.log('--- Initial Build ---');
  compileSlides();
  startWatcher();
  startServer();
}

if (require.main === module) {
  init();
}

module.exports = {
  ROOT_DIR,
  SLIDES_DIR,
  PUBLIC_DIR,
  getServerParams,
  compileSlides,
  startWatcher,
  startServer,
  init
};
