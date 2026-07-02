# Exporter module for COC IIoT Talk 2026
# This module provides Docker-based PDF export functionality for Reveal.js presentations

from .config import ExporterConfig, ExportResult, CommandExecution, ImageReference
from .asciidoc_parser import parse_images_from_adoc, validate_and_resolve_images, parse_slides_and_notes
from .html_builder import prepare_build_directory, fetch_revealjs_assets, compile_asciidoc_to_html
from .docker_utils import check_docker_availability, run_docker_command, format_docker_volume_path
from .http_server import TempHTTPServer, wait_for_server_healthy
from .decktape_exporter import export_slides_with_decktape
from .pdf_utils import generate_notes_pdf_handout
from .reporting import write_export_report

__version__ = "1.0.0"
__all__ = [
    'ExporterConfig', 'ExportResult', 'CommandExecution', 'ImageReference',
    'parse_images_from_adoc', 'validate_and_resolve_images', 'parse_slides_and_notes',
    'prepare_build_directory', 'fetch_revealjs_assets', 'compile_asciidoc_to_html',
    'check_docker_availability', 'run_docker_command', 'format_docker_volume_path',
    'TempHTTPServer', 'wait_for_server_healthy',
    'export_slides_with_decktape',
    'generate_notes_pdf_handout',
    'write_export_report'
]