"""
Background HTTP server for serving the generated Reveal.js presentation.
"""

import http.server
import logging
import socket
import socketserver
import threading
import time
import urllib.request
from pathlib import Path

logger = logging.getLogger("exporter")

class TempHTTPServer:
    """A background HTTP server serving files from a specified directory."""
    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.port = None
        self.server = None
        self.thread = None

    def __enter__(self):
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(kwargs.pop('directory')), **kwargs)
                
            def log_message(self, format, *args):
                # Suppress normal logging to keep CLI output clean
                pass

        # Simple context factory to pass directory parameter
        def handler_factory(*args, **kwargs):
            return Handler(*args, directory=self.directory, **kwargs)

        # Bind to port 0 to let the OS assign a free dynamic port
        self.server = socketserver.TCPServer(("0.0.0.0", 0), handler_factory)
        self.port = self.server.socket.getsockname()[1]
        
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info("Started background HTTP server on port %d serving directory %s", self.port, self.directory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            logger.info("Stopping HTTP server...")
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("HTTP server stopped successfully.")

def wait_for_server_healthy(port: int, path: str = "presentation.html", timeout: float = 10.0) -> None:
    """Pings the local HTTP server until it responds or timeouts."""
    url = f"http://127.0.0.1:{port}/{path}"
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    logger.debug("Server health check succeeded at %s", url)
                    return
        except Exception:
            pass
        time.sleep(0.2)
        
    raise RuntimeError(f"HTTP server at {url} did not become healthy within {timeout} seconds.")
