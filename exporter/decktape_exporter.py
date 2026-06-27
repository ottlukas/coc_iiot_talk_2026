"""
Handles PDF slide export using Decktape inside Docker.
"""

import logging
import platform
from pathlib import Path
from exporter.config import ExporterConfig, CommandExecution
from exporter.docker_utils import run_docker_command, format_docker_volume_path

logger = logging.getLogger("exporter")

def get_decktape_connection_settings(port: int) -> tuple[str, list[str]]:
    """
    Get the appropriate URL and docker network/hosts arguments for Decktape.
    - Linux: uses 127.0.0.1 with --network host
    - Windows/macOS: uses host.docker.internal with host-gateway mapping
    """
    sys_name = platform.system().lower()
    
    if sys_name == "linux":
        url = f"http://127.0.0.1:{port}/presentation.html"
        docker_args = ["--network", "host"]
        logger.debug("Linux detected: using host network and localhost URL for Decktape.")
    else:
        url = f"http://host.docker.internal:{port}/presentation.html"
        docker_args = ["--add-host", "host.docker.internal:host-gateway"]
        logger.debug("Non-Linux (%s) detected: using host.docker.internal gateway mapping for Decktape.", platform.system())
        
    return url, docker_args

def export_slides_with_decktape(
    config: ExporterConfig,
    server_port: int,
    output_filename: str = "presentation.pdf"
) -> CommandExecution:
    """
    Runs Decktape in Docker against the local served presentation URL.
    Writes the PDF directly to the output directory.
    """
    logger.info("Starting Decktape slide-only PDF export...")
    
    target_url, connection_args = get_decktape_connection_settings(server_port)
    output_dir_posix = format_docker_volume_path(config.output_dir)
    
    # Ensure host output dir exists
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "docker", "run", "--rm",
        *connection_args,
        "-v", f"{output_dir_posix}:/slides",
        config.docker_image_decktape,
        "reveal",
        "--size", config.viewport_size,
        "--pause", str(config.decktape_pause),
        target_url,
        f"/slides/{output_filename}"
    ]
    
    logger.debug("Running Decktape command: %s", " ".join(cmd))
    exec_result = run_docker_command(cmd, timeout=config.timeout)
    
    if exec_result.exit_code == 0:
        logger.info("Decktape slide export completed successfully. Output written to %s", config.output_dir / output_filename)
    else:
        logger.error("Decktape slide export failed with exit code %d: %s", exec_result.exit_code, exec_result.stderr)
        
    return exec_result
