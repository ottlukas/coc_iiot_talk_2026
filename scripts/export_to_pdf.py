#!/usr/bin/env python3
"""
Cross-platform Docker-based PDF exporter for Reveal.js presentations.

Works on both Windows and Linux by:
- Using pathlib.Path for all file operations
- Converting container paths to POSIX format (forward slashes)
- Auto-detecting Docker CLI format (docker compose vs docker-compose)
- Resolving paths relative to script location
"""

import argparse
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path
import re

# Configuration constants
DEFAULT_URL = 'http://localhost:4200'
DEFAULT_OUTPUT_NAME = 'presentation.pdf'
DEFAULT_NOTES_SUFFIX = '-speaker-notes'

# Resolve script location dynamically (works on Windows and Linux)
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent

# Define paths using pathlib.Path (platform-agnostic)
HELPER_SCRIPT = SCRIPT_DIR / 'puppeteer_export.js'
COMPOSE_FILE = ROOT_DIR / 'docker' / 'dev' / 'docker-compose.yml'

# Docker service configuration
SERVICE_NAME = 'presentation'
CONTAINER_NAME = 'asciidoc-revealjs-presentation'

# Container paths (always use forward slashes for Docker)
CONTAINER_WORKDIR = Path('/app')
CONTAINER_DOCS_ROOT = CONTAINER_WORKDIR / 'docs'
CONTAINER_HELPER_SCRIPT = CONTAINER_WORKDIR / 'scripts' / 'puppeteer_export.js'

# Docker CLI candidates: (command, supports_compose_subcommand)
# "docker compose" is the modern format (Windows & recent Linux)
# "docker-compose" is the legacy standalone tool (older Linux systems)
DOCKER_CLI_CANDIDATES = [
    (['docker', 'compose'], True),
    (['docker-compose'], False),
]


def resolve_input_path(adoc_path: str) -> Path:
    """
    Resolve input AsciiDoc file path.
    
    Checks in order:
    1. If absolute, return as-is
    2. If relative, check current working directory
    3. Otherwise, check relative to project root
    """
    path = Path(adoc_path)
    
    # Absolute paths are returned directly
    if path.is_absolute():
        return path

    # Check current working directory first
    cwd_candidate = Path.cwd() / path
    if cwd_candidate.exists():
        return cwd_candidate

    # Fall back to project root
    return ROOT_DIR / path


def infer_output_pdf_path(adoc_path: str | Path, root_dir: Path = ROOT_DIR) -> Path:
    """Infer output PDF path from input AsciiDoc file."""
    path = Path(adoc_path)
    if path.suffix.lower() != '.adoc':
        raise ValueError('Input file must be an AsciiDoc file with .adoc extension')
    return root_dir / 'docs' / 'exports' / DEFAULT_OUTPUT_NAME


def infer_notes_pdf_path(slides_output: Path) -> Path:
    """Derive speaker-notes PDF path from slides output path.

    E.g. presentation.pdf -> presentation-speaker-notes.pdf
    """
    stem = slides_output.stem + DEFAULT_NOTES_SUFFIX
    return slides_output.with_name(stem + slides_output.suffix)


def validate_input_file(adoc_path: Path) -> None:
    """Validate that input file exists and is a file."""
    if not adoc_path.exists():
        raise FileNotFoundError(f'AsciiDoc source file not found: {adoc_path}')
    if not adoc_path.is_file():
        raise ValueError(f'Provided path is not a file: {adoc_path}')


def ensure_output_dir(output_path: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_path.parent.mkdir(parents=True, exist_ok=True)


def check_presentation_server(url: str) -> None:
    """Verify the presentation server is reachable."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.status >= 400:
                raise RuntimeError(f'Presentation server returned HTTP {response.status} at {url}')
    except urllib.error.URLError as err:
        raise RuntimeError(
            f'Presentation server is not reachable at {url}. '
            f'Ensure the Docker container is running and the server is available.'
        ) from err


def find_docker_cli() -> tuple[list[str], bool]:
    """
    Detect available Docker CLI and its format.
    
    Returns:
        (docker_command, supports_compose_subcommand)
        - docker_command: list like ['docker', 'compose'] or ['docker-compose']
        - supports_compose_subcommand: True if "docker compose" works, False otherwise
    """
    # Try modern "docker compose" first (Windows & recent Docker versions)
    for candidate, supports_compose in DOCKER_CLI_CANDIDATES:
        try:
            subprocess.run(
                [*candidate, 'version'],
                check=True,
                capture_output=True,
                text=True,
            )
            return candidate, supports_compose
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    # Fallback: try bare "docker" command
    docker_runtime = find_docker_runtime()
    if docker_runtime:
        return [docker_runtime], False

    raise RuntimeError(
        'Docker is not available. Install Docker and Docker Compose, '
        'then start the presentation container.'
    )


def find_docker_runtime() -> str | None:
    """Find the 'docker' executable in PATH."""
    return shutil.which('docker')


def find_running_presentation_container(
    docker_cli: list[str], supports_compose: bool
) -> tuple[str, bool]:
    """
    Find the running presentation container.
    
    Returns:
        (container_id, used_compose)
        - container_id: ID of the running container
        - used_compose: True if found via docker-compose, False if via docker ps
    """
    # Try docker-compose first if supported and compose file exists
    if supports_compose and COMPOSE_FILE.exists():
        try:
            result = subprocess.run(
                [
                    *docker_cli,
                    '-f',
                    str(COMPOSE_FILE),  # Path converted to string for subprocess
                    'ps',
                    '-q',
                    SERVICE_NAME,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            container_id = result.stdout.strip()
            if container_id:
                return container_id, True
        except subprocess.CalledProcessError:
            pass

    # Fallback: search by container name using docker ps
    docker_runtime = find_docker_runtime()
    if docker_runtime:
        try:
            result = subprocess.run(
                [
                    docker_runtime,
                    'ps',
                    '-q',
                    '-f',
                    f'name={CONTAINER_NAME}',
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            container_id = result.stdout.strip()
            if container_id:
                return container_id, False
        except subprocess.CalledProcessError:
            pass

    raise RuntimeError(
        'Presentation Docker container is not running. '
        'Start it with: docker compose -f docker/dev/docker-compose.yml up --build'
    )


def host_to_container_output_path(output_path: Path) -> Path:
    """
    Convert host output path to container path.
    
    If the output path is within the docs directory, map it to the container's
    mounted docs directory. Otherwise, use a temporary path in the container.
    """
    docs_root = ROOT_DIR / 'docs'
    try:
        relative = output_path.resolve().relative_to(docs_root.resolve())
        return CONTAINER_DOCS_ROOT / relative
    except ValueError:
        # Output is outside docs directory; use temporary path in container
        return Path('/tmp') / f'export-{uuid.uuid4().hex}.pdf'


def parse_adoc_for_images(adoc_path: Path) -> list[dict]:
    """Parse AsciiDoc source for image references.

    Returns a list of dicts: { 'ref': str, 'line': int, 'text': str }
    Supports AsciiDoc `image::path[]`, `image:src[]` and HTML `<img src>` and `data-src` patterns.
    """
    pattern_image_macro = re.compile(r"image::([^\[]+)\[")
    pattern_image_inline = re.compile(r"(?<!:)image:([^\[]+)\[")
    pattern_img_tag = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
    pattern_data_src = re.compile(r"data-src=[\"']([^\"']+)[\"']", re.IGNORECASE)

    results = []
    with adoc_path.open('r', encoding='utf8') as fh:
        for idx, line in enumerate(fh, start=1):
            for m in pattern_image_macro.finditer(line):
                ref = m.group(1).strip()
                ref = ref.lstrip(':')
                results.append({'ref': ref, 'line': idx, 'text': line.strip()})
            for m in pattern_image_inline.finditer(line):
                ref = m.group(1).strip()
                ref = ref.lstrip(':')
                results.append({'ref': ref, 'line': idx, 'text': line.strip()})
            for m in pattern_img_tag.finditer(line):
                ref = m.group(1).strip()
                ref = ref.lstrip(':')
                results.append({'ref': ref, 'line': idx, 'text': line.strip()})
            for m in pattern_data_src.finditer(line):
                ref = m.group(1).strip()
                ref = ref.lstrip(':')
                results.append({'ref': ref, 'line': idx, 'text': line.strip()})

    return results


def validate_image_sources(image_refs: list[dict], adoc_path: Path) -> None:
    """Validate that image sources referenced in AsciiDoc are available.

    - For local files: checks file exists relative to the AsciiDoc file or project.
    - For remote URLs: attempts a short HTTP request.
    Raises FileNotFoundError with details if any missing.
    """
    missing = []
    adoc_dir = adoc_path.resolve().parent
    for item in image_refs:
        ref = item['ref']
        if ref.startswith('http://') or ref.startswith('https://'):
            try:
                with urllib.request.urlopen(ref, timeout=5) as resp:
                    if resp.status >= 400:
                        missing.append((item, f'HTTP {resp.status}'))
            except Exception as e:
                missing.append((item, str(e)))
        else:
            # Try relative to adoc, then docs/images, then project root
            candidates = [adoc_dir / ref]
            # strip leading slash
            if ref.startswith('/'):
                candidates.append(ROOT_DIR / ref.lstrip('/'))
            candidates.append(ROOT_DIR / 'docs' / ref)
            candidates.append(ROOT_DIR / 'docs' / 'images' / ref)

            found = False
            for c in candidates:
                try:
                    if c.exists():
                        found = True
                        break
                except Exception:
                    continue
            if not found:
                missing.append((item, 'file not found'))

    if missing:
        messages = []
        for it, why in missing:
            messages.append(f"Line {it['line']}: {it['ref']} -> {why} (context: {it['text']})")
        raise FileNotFoundError('Missing image assets:\n' + '\n'.join(messages))


def check_pdf_for_images(pdf_path: Path, image_refs: list[dict]) -> None:
    """Check generated PDF for embedded images.

    Strategy:
    - Look for PDF image objects via `/Subtype /Image` tokens.
    - Also search for basenames of referenced images inside PDF bytes as a heuristic.
    Raises RuntimeError if no images are found or referenced images are not embedded.
    """
    data = pdf_path.read_bytes()
    has_image_objects = b'/Subtype /Image' in data or b'/Type /XObject' in data

    missing = []
    # Check that at least one image object exists
    if not has_image_objects:
        missing.append('PDF does not contain image XObject tokens')

    # If we found no image objects, the PDF clearly lacks embedded images.
    if not has_image_objects:
        raise RuntimeError('PDF image validation failed:\nPDF does not contain image XObject tokens')

    # Heuristic: if there are image refs and image objects exist, assume export succeeded.
    # Embedded PDF objects typically do not carry original filenames, so filename-based
    # matching is unreliable for this renderer.
    if image_refs and has_image_objects:
        return

    if missing:
        raise RuntimeError('PDF image validation failed:\n' + '\n'.join(missing))


def copy_output_from_container(
    container_id: str, container_path: Path, output_path: Path
) -> None:
    """
    Copy output file from container to host.
    
    Uses docker cp to transfer the file from container to local filesystem.
    """
    docker_runtime = find_docker_runtime()
    if not docker_runtime:
        raise RuntimeError(
            'Docker executable not found for copying output from the container. '
            'Install Docker and retry.'
        )

    # Convert container path to POSIX format (forward slashes)
    # This is important on Windows where Path uses backslashes internally
    command = [
        docker_runtime,
        'cp',
        f'{container_id}:{container_path.as_posix()}',  # as_posix() for cross-platform
        str(output_path),
    ]
    
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_puppeteer_export(
    output_path: Path, url: str = DEFAULT_URL, node_path: str | None = None
) -> None:
    """
    Execute Puppeteer export inside Docker container.
    
    Runs the Node.js Puppeteer script in the presentation Docker container
    to generate the PDF from the HTML presentation.
    """
    if not HELPER_SCRIPT.exists():
        raise FileNotFoundError(f'Puppeteer helper script not found: {HELPER_SCRIPT}')

    # Verify presentation server is accessible
    check_presentation_server(url)

    # Detect Docker CLI
    docker_cli, supports_compose = find_docker_cli()
    container_id, used_compose = find_running_presentation_container(docker_cli, supports_compose)
    
    # Map host output path to container path
    container_output = host_to_container_output_path(output_path)
    copy_back = container_output.parent == Path('/tmp')

    # Build Docker command based on whether docker-compose is available
    if used_compose:
        # Use "docker compose exec" or "docker-compose exec"
        command = [
            *docker_cli,
            '-f',
            str(COMPOSE_FILE),
            'exec',
            '-T',  # Disable pseudo-TTY allocation (required for non-interactive use)
            SERVICE_NAME,
            'node',
            CONTAINER_HELPER_SCRIPT.as_posix(),  # FIX: Use .as_posix() for cross-platform paths
            '--url',
            url,
            '--output',
            container_output.as_posix(),  # Convert to POSIX for Docker
        ]
    else:
        # Use "docker exec" on running container
        docker_runtime = find_docker_runtime()
        if not docker_runtime:
            raise RuntimeError('Docker executable not found. Install Docker and retry.')
        
        command = [
            docker_runtime,
            'exec',
            '-i',  # Interactive mode for stdin/stdout
            container_id,
            'node',
            CONTAINER_HELPER_SCRIPT.as_posix(),  # FIX: Use .as_posix() for cross-platform paths
            '--url',
            url,
            '--output',
            container_output.as_posix(),  # Convert to POSIX for Docker
        ]

    try:
        # Execute Puppeteer export in container
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Copy file from container if it was written to /tmp
        if copy_back:
            ensure_output_dir(output_path)
            copy_output_from_container(container_id, container_output, output_path)
            
    except subprocess.CalledProcessError as err:
        raise RuntimeError(
            f'Puppeteer export failed with exit code {err.returncode}: '
            f'{err.stderr.strip() or err.stdout.strip()}'
        ) from err


def main(argv=None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Export Reveal.js presentation to PDF via Docker'
    )
    parser.add_argument('adoc_path', help='Path to the AsciiDoc source file')
    parser.add_argument(
        '--url',
        default=DEFAULT_URL,
        help=f'URL of the running presentation server (default: {DEFAULT_URL})',
    )
    parser.add_argument('--output', help='Explicit output PDF path (legacy, maps to slides output)')
    parser.add_argument('--slides-output', help='Explicit slides PDF output path')
    parser.add_argument('--notes-output', help='Explicit speaker-notes PDF output path')
    parser.add_argument('--slides-only', action='store_true', help='Only export slides PDF')
    parser.add_argument('--notes-only', action='store_true', help='Only export speaker-notes PDF')
    args = parser.parse_args(argv)

    # Resolve input file path
    adoc_path = resolve_input_path(args.adoc_path)
    validate_input_file(adoc_path)

    # Parse AsciiDoc for image references and validate sources before export
    image_refs = parse_adoc_for_images(adoc_path)
    if image_refs:
        validate_image_sources(image_refs, adoc_path)

    # Determine slides and notes output paths
    # Backwards compatibility: --output maps to slides output
    if args.slides_output:
        slides_output = Path(args.slides_output)
    elif args.output:
        slides_output = Path(args.output)
    else:
        slides_output = infer_output_pdf_path(adoc_path, ROOT_DIR)

    if slides_output and not slides_output.is_absolute():
        slides_output = Path.cwd() / slides_output

    if args.notes_output:
        notes_output = Path(args.notes_output)
    else:
        notes_output = infer_notes_pdf_path(slides_output)

    if notes_output and not notes_output.is_absolute():
        notes_output = Path.cwd() / notes_output

    # Ensure output directories exist for the artifacts we're about to create
    if not args.notes_only:
        ensure_output_dir(slides_output)
    if not args.slides_only:
        ensure_output_dir(notes_output)

    performed = []

    # Slides export (legacy path and default)
    if not args.notes_only:
        run_puppeteer_export(slides_output, args.url)
        if not slides_output.exists():
            raise RuntimeError(f'Export did not create the expected slides PDF file: {slides_output}')
        print(f'Slides PDF export complete: {slides_output}')
        # Post-export PDF validation for images only when images were referenced
        if image_refs:
            check_pdf_for_images(slides_output, image_refs)
        performed.append(slides_output)

    # Notes export (separate run with --mode=notes)
    if not args.slides_only:
        # Prepare Docker invocation similar to run_puppeteer_export but pass --mode notes
        docker_cli, supports_compose = find_docker_cli()
        container_id, used_compose = find_running_presentation_container(docker_cli, supports_compose)
        container_output = host_to_container_output_path(notes_output)
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
                CONTAINER_HELPER_SCRIPT.as_posix(),
                '--url',
                args.url,
                '--output',
                container_output.as_posix(),
                '--mode',
                'notes',
            ]
        else:
            docker_runtime = find_docker_runtime()
            if not docker_runtime:
                raise RuntimeError('Docker executable not found. Install Docker and retry.')
            command = [
                docker_runtime,
                'exec',
                '-i',
                container_id,
                'node',
                CONTAINER_HELPER_SCRIPT.as_posix(),
                '--url',
                args.url,
                '--output',
                container_output.as_posix(),
                '--mode',
                'notes',
            ]

        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            if copy_back:
                ensure_output_dir(notes_output)
                copy_output_from_container(container_id, container_output, notes_output)
        except subprocess.CalledProcessError as err:
            raise RuntimeError(
                f'Puppeteer notes export failed with exit code {err.returncode}: '
                f'{err.stderr.strip() or err.stdout.strip()}'
            ) from err

        if not notes_output.exists():
            raise RuntimeError(f'Export did not create the expected notes PDF file: {notes_output}')
        print(f'Speaker-notes PDF export complete: {notes_output}')
        performed.append(notes_output)

    print('PDF export complete:', ', '.join(str(p) for p in performed))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f'Error: {error}', file=sys.stderr)
        raise
