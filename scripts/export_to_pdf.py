#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

DEFAULT_URL = 'http://localhost:4200'
DEFAULT_OUTPUT_NAME = 'presentation.pdf'
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
HELPER_SCRIPT = SCRIPT_DIR / 'puppeteer_export.js'
COMPOSE_FILE = ROOT_DIR / 'docker' / 'dev' / 'docker-compose.yml'
SERVICE_NAME = 'presentation'
CONTAINER_NAME = 'asciidoc-revealjs-presentation'
CONTAINER_WORKDIR = Path('/app')
CONTAINER_DOCS_ROOT = CONTAINER_WORKDIR / 'docs'
CONTAINER_HELPER_SCRIPT = CONTAINER_WORKDIR / 'scripts' / 'puppeteer_export.js'
DOCKER_CLI_CANDIDATES = [(['docker', 'compose'], True), (['docker-compose'], False)]


def resolve_input_path(adoc_path: str) -> Path:
    path = Path(adoc_path)
    if path.is_absolute():
        return path

    cwd_candidate = Path.cwd() / path
    if cwd_candidate.exists():
        return cwd_candidate

    return ROOT_DIR / path


def infer_output_pdf_path(adoc_path: str | Path, root_dir: Path = ROOT_DIR) -> Path:
    path = Path(adoc_path)
    if path.suffix.lower() != '.adoc':
        raise ValueError('Input file must be an AsciiDoc file with .adoc extension')
    return root_dir / 'docs' / 'exports' / DEFAULT_OUTPUT_NAME


def validate_input_file(adoc_path: Path) -> None:
    if not adoc_path.exists():
        raise FileNotFoundError(f'AsciiDoc source file not found: {adoc_path}')
    if not adoc_path.is_file():
        raise ValueError(f'Provided path is not a file: {adoc_path}')


def ensure_output_dir(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)


def check_presentation_server(url: str) -> None:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status >= 400:
                raise RuntimeError(f'Presentation server returned HTTP {response.status} at {url}')
    except urllib.error.URLError as err:
        raise RuntimeError(
            f'Presentation server is not reachable at {url}. Ensure the Docker container is running and the server is available.'
        ) from err


def find_docker_cli() -> tuple[list[str], bool]:
    for candidate, supports_compose in DOCKER_CLI_CANDIDATES:
        try:
            subprocess.run([*candidate, 'version'], check=True, capture_output=True, text=True)
            return candidate, supports_compose
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    docker_runtime = find_docker_runtime()
    if docker_runtime:
        return [docker_runtime], False

    raise RuntimeError(
        'Docker is not available. Install Docker and Docker Compose, then start the presentation container.'
    )


def find_docker_runtime() -> str | None:
    return shutil.which('docker')


def find_running_presentation_container(docker_cli: list[str], supports_compose: bool) -> tuple[str, bool]:
    if supports_compose and COMPOSE_FILE.exists():
        result = subprocess.run(
            [*docker_cli, '-f', str(COMPOSE_FILE), 'ps', '-q', SERVICE_NAME],
            check=True,
            capture_output=True,
            text=True,
        )
        container_id = result.stdout.strip()
        if container_id:
            return container_id, True

    docker_runtime = find_docker_runtime()
    if docker_runtime:
        result = subprocess.run(
            [docker_runtime, 'ps', '-q', '-f', f'name={CONTAINER_NAME}'],
            check=True,
            capture_output=True,
            text=True,
        )
        container_id = result.stdout.strip()
        if container_id:
            return container_id, False

    raise RuntimeError(
        'Presentation Docker container is not running. Start it with `docker compose -f docker/dev/docker-compose.yml up --build`.'
    )


def host_to_container_output_path(output_path: Path) -> Path:
    docs_root = ROOT_DIR / 'docs'
    try:
        relative = output_path.resolve().relative_to(docs_root.resolve())
        return CONTAINER_DOCS_ROOT / relative
    except ValueError:
        return Path('/tmp') / f'export-{uuid.uuid4().hex}.pdf'


def copy_output_from_container(container_id: str, container_path: Path, output_path: Path) -> None:
    docker_runtime = find_docker_runtime()
    if not docker_runtime:
        raise RuntimeError(
            'Docker executable not found for copying output from the container. Install Docker and retry.'
        )

    command = [
        docker_runtime,
        'cp',
        f'{container_id}:{container_path}',
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_puppeteer_export(output_path: Path, url: str = DEFAULT_URL, node_path: str | None = None) -> None:
    if not HELPER_SCRIPT.exists():
        raise FileNotFoundError(f'Puppeteer helper script not found: {HELPER_SCRIPT}')

    check_presentation_server(url)

    docker_cli, supports_compose = find_docker_cli()
    container_id, used_compose = find_running_presentation_container(docker_cli, supports_compose)
    container_output = host_to_container_output_path(output_path)
    copy_back = container_output.parent == Path('/tmp')

    if used_compose:
        command = [
            *docker_cli,
            '-f',
            str(COMPOSE_FILE),
            'exec',
            '-T',
            SERVICE_NAME,
            'node',
            str(CONTAINER_HELPER_SCRIPT),
            '--url',
            url,
            '--output',
            str(container_output),
        ]
    else:
        docker_runtime = find_docker_runtime()
        if not docker_runtime:
            raise RuntimeError(
                'Docker executable not found. Install Docker and retry.'
            )
        command = [
            docker_runtime,
            'exec',
            '-i',
            container_id,
            'node',
            str(CONTAINER_HELPER_SCRIPT),
            '--url',
            url,
            '--output',
            str(container_output),
        ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        if copy_back:
            ensure_output_dir(output_path)
            copy_output_from_container(container_id, container_output, output_path)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(
            f'Puppeteer export failed with exit code {err.returncode}: {err.stderr.strip() or err.stdout.strip()}'
        ) from err


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Export Reveal.js presentation to PDF')
    parser.add_argument('adoc_path', help='Path to the AsciiDoc source file')
    parser.add_argument('--url', default=DEFAULT_URL, help='URL of the running presentation server')
    parser.add_argument('--output', help='Explicit output PDF path')
    args = parser.parse_args(argv)

    adoc_path = resolve_input_path(args.adoc_path)
    validate_input_file(adoc_path)

    output_path = Path(args.output) if args.output else infer_output_pdf_path(adoc_path, ROOT_DIR)
    if args.output and not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    ensure_output_dir(output_path)

    run_puppeteer_export(output_path, args.url)

    if not output_path.exists():
        raise RuntimeError(f'Export did not create the expected PDF file: {output_path}')

    print(f'PDF export complete: {output_path}')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        raise
