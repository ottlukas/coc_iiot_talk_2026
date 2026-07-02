"""
Docker command execution and platform-aware volume helper utilities.
"""

import logging
import platform
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple
from . config import CommandExecution

logger = logging.getLogger("exporter")

def find_docker_executable() -> str:
    """Find the path of the docker executable."""
    exe = shutil.which("docker")
    if not exe:
        raise RuntimeError("Docker command-line tool not found. Please install Docker.")
    return exe

def check_docker_availability() -> None:
    """Check if docker is installed and running."""
    docker_exe = find_docker_executable()
    try:
        # Run docker info to verify the daemon is running
        subprocess.run(
            [docker_exe, "info"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Docker daemon is not running or accessible: {e.stderr.strip()}"
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Docker daemon check timed out. Is Docker running?") from e

def find_docker_compose_cli() -> Tuple[List[str], bool]:
    """
    Detects which docker compose CLI to use.
    Returns:
        (docker_compose_cmd_list, is_compose_v2)
    """
    docker_exe = find_docker_executable()
    # Try modern "docker compose" (V2)
    try:
        res = subprocess.run(
            [docker_exe, "compose", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if res.returncode == 0:
            return [docker_exe, "compose"], True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Try legacy "docker-compose" (V1)
    legacy_exe = shutil.which("docker-compose")
    if legacy_exe:
        try:
            res = subprocess.run(
                [legacy_exe, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if res.returncode == 0:
                return [legacy_exe], False
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    # Fallback to plain docker if compose is not found (though exporter defaults to raw docker runs)
    return [docker_exe], False

def format_docker_volume_path(local_path: Path) -> str:
    """
    Convert a host path to a POSIX-compliant format for Docker volume mounts.
    On Windows, resolves drive letters and uses forward slashes (e.g. C:/path/to/dir).
    """
    resolved = local_path.resolve()
    # Path.as_posix() converts backslashes to forward slashes.
    # Docker on Windows handles "C:/path/to/dir" perfectly in volume mounts.
    return resolved.as_posix()

def run_docker_command(
    command_args: List[str],
    timeout: int = 120
) -> CommandExecution:
    """
    Run a docker command and capture execution metrics.
    """
    logger.debug("Executing command: %s", " ".join(command_args))
    try:
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
    except subprocess.TimeoutExpired as e:
        logger.error("Command timed out: %s", " ".join(command_args))
        stdout = e.stdout or ""
        stderr = (e.stderr or "") + f"\n[ERROR] Command timed out after {timeout} seconds"
        exit_code = -1
    except Exception as e:
        logger.error("Command execution failed: %s", str(e))
        stdout = ""
        stderr = f"[ERROR] Execution failed: {str(e)}"
        exit_code = -2

    return CommandExecution(
        command=command_args,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr
    )
