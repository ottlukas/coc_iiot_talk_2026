"""
Configuration options and data models for the presentation PDF exporter.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any

@dataclass
class ExporterConfig:
    """Configuration options for the PDF exporter."""
    source_file: Path
    images_dir: Path
    stylesheet_file: Path
    output_dir: Path
    docker_image_decktape: str = "astefanutti/decktape"
    docker_image_asciidoctor: str = "asciidoctor/docker-asciidoctor"
    viewport_size: str = "1920x1080"
    decktape_pause: int = 1000
    timeout: int = 120
    ignore_missing_images: bool = False
    include_empty_notes: bool = False
    verbose: bool = False

@dataclass
class ImageReference:
    """Represents an image reference found in the AsciiDoc source."""
    ref_path: str
    line_number: int
    context_line: str
    is_valid: bool = False
    error_message: str = ""

@dataclass
class CommandExecution:
    """Details of a shell command execution."""
    command: List[str]
    exit_code: int
    stdout: str
    stderr: str

@dataclass
class ExportResult:
    """Results of the export execution to generate the report."""
    status: str = "failed"
    error_message: str = ""
    source_file: str = ""
    outputs: Dict[str, str] = field(default_factory=dict)
    images_validation: Dict[str, Any] = field(default_factory=dict)
    commands_executed: List[CommandExecution] = field(default_factory=list)
