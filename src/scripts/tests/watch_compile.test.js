const fs = require('fs');
const http = require('http');
const path = require('path');
const { spawn } = require('child_process');
const { PUBLIC_DIR, getServerParams, compileSlides } = require('../watch');

const PROJECT_ROOT = path.resolve(__dirname, '../../..');
const SERVER_URL = 'http://127.0.0.1:4200';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function waitForServer(url, timeout = 15000) {
  const end = Date.now() + timeout;

  return new Promise((resolve, reject) => {
    const attempt = () => {
      if (Date.now() > end) {
        return reject(new Error(`Server did not respond with 200 OK within ${timeout}ms`));
      }

      http.get(url, (res) => {
        if (res.statusCode === 200) {
          res.resume();
          return resolve(res);
        }

        res.resume();
        setTimeout(attempt, 500);
      }).on('error', () => {
        setTimeout(attempt, 500);
      });
    };

    attempt();
  });
}

describe('Presentation compile and dev server', () => {
  let serverProcess;

  beforeAll(async () => {
    // Ensure the public directory exists before starting the server.
    fs.mkdirSync(PUBLIC_DIR, { recursive: true });

    serverProcess = spawn('node', ['src/scripts/watch.js'], {
      cwd: PROJECT_ROOT,
      env: { ...process.env, PORT: '4200' },
      stdio: ['ignore', 'pipe', 'pipe']
    });

    serverProcess.stdout.on('data', (data) => {
      process.stdout.write(`[watch.js] ${data}`);
    });
    serverProcess.stderr.on('data', (data) => {
      process.stderr.write(`[watch.js] ${data}`);
    });

    await waitForServer(`${SERVER_URL}/`);
  }, 30000);

  afterAll(async () => {
    if (serverProcess) {
      serverProcess.kill('SIGTERM');
      await sleep(500);
    }
  });

  it('compiles presentation to public/index.html', async () => {
    compileSlides();
    const indexHtmlPath = path.join(PUBLIC_DIR, 'index.html');

    expect(fs.existsSync(indexHtmlPath)).toBe(true);
    const stat = fs.statSync(indexHtmlPath);
    expect(stat.isFile()).toBe(true);
  }, 30000);

  it('exposes live-server configuration with correct root and file', () => {
    const serverParams = getServerParams();

    expect(serverParams.root).toBe(PUBLIC_DIR);
    expect(serverParams.file).toBe('index.html');
    expect(fs.existsSync(path.join(serverParams.root, serverParams.file))).toBe(true);
  });

  it('responds to GET / with 200 OK', async () => {
    const response = await waitForServer(`${SERVER_URL}/`);
    expect(response.statusCode).toBe(200);
  }, 30000);
});
